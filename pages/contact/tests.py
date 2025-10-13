from __future__ import annotations

"""Tests for the contact form and view.

Covers anti-spam (honeypot, timing, token), validation, and email sending.
Uses Django's locmem email backend for assertions.
"""

import re
import time
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core import mail
from unittest.mock import patch


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="Pathogens Portal <no-reply@example.org>",
)
class ContactFormTests(TestCase):
    """Integration tests for the contact view and form."""
    def setUp(self) -> None:
        """Initialise test client for each test."""
        self.client = Client()

    def _get_tokens_from_response(self, response):
        """Extract hidden anti-spam token values from rendered HTML.

        Args:
            response: The GET response containing the form.

        Returns:
            Tuple of (timestamp_token, double_submit_token).
        """
        content = response.content.decode()
        dsc_match = re.search(r'name="contact_dsc" value="([^"]+)"', content)
        ts_match = re.search(r'name="contact_ts" value="([^"]+)"', content)
        dsc = dsc_match.group(1) if dsc_match else None
        ts = ts_match.group(1) if ts_match else None
        return ts, dsc

    def test_get_renders_form_and_sets_cookie(self):
        """GET should render the form and set the double-submit cookie."""
        url = reverse("contact:contact")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        # Cookie set
        self.assertIn("contact_dsc", resp.cookies)
        # Hidden fields present
        ts, dsc = self._get_tokens_from_response(resp)
        self.assertIsNotNone(ts)
        self.assertIsNotNone(dsc)

    def test_csrf_missing_returns_403(self):
        """POST without CSRF token should be rejected when checks are enforced."""
        client = Client(enforce_csrf_checks=True)
        url = reverse("contact:contact")
        # No CSRF token provided on POST
        resp = client.post(url, data={})
        self.assertEqual(resp.status_code, 403)

    def test_happy_path_sends_email(self):
        """Valid submission sends a single email with expected subject."""
        url = reverse("contact:contact")
        resp = self.client.get(url)
        ts, dsc = self._get_tokens_from_response(resp)
        # Wait a bit to pass min timing of 2s
        time.sleep(2)
        post = {
            "name": "Alice",
            "email": "alice@example.org",
            "message": "This is a valid message with minimal content.",
            "suggestion": "on",
            "website": "",
            "contact_ts": ts,
            "contact_dsc": dsc,
        }
        resp2 = self.client.post(url, data=post, follow=True)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(
            "[Contact] Contact and suggestions form", mail.outbox[0].subject
        )
        # Success message present after redirect
        self.assertIn(b"Thanks! Your message was sent", resp2.content)

    def test_honeypot_blocks(self):
        """Filling the honeypot field must block submission."""
        url = reverse("contact:contact")
        resp = self.client.get(url)
        ts, dsc = self._get_tokens_from_response(resp)
        post = {
            "name": "Alice",
            "email": "alice@example.org",
            "message": "Valid message body that is long enough.",
            "website": "spam",
            "contact_ts": ts,
            "contact_dsc": dsc,
        }
        resp2 = self.client.post(url, data=post)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_timing_too_fast_blocks(self):
        """Posting faster than 2s after GET should be blocked."""
        url = reverse("contact:contact")
        resp = self.client.get(url)
        ts, dsc = self._get_tokens_from_response(resp)
        post = {
            "name": "Alice",
            "email": "alice@example.org",
            "message": "Valid message body that is long enough.",
            "suggestion": "on",
            "website": "",
            "contact_ts": ts,
            "contact_dsc": dsc,
        }
        resp2 = self.client.post(url, data=post)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    @patch("pages.contact.views.EmailMessage.send", side_effect=Exception("SMTP down"))
    def test_smtp_failure_path(self, _mock_send):
        """If SMTP fails, display generic error and do not send email."""
        url = reverse("contact:contact")
        resp = self.client.get(url)
        ts, dsc = self._get_tokens_from_response(resp)
        time.sleep(2)
        post = {
            "name": "Alice",
            "email": "alice@example.org",
            "message": "Valid message body that is long enough.",
            "suggestion": "on",
            "website": "",
            "contact_ts": ts,
            "contact_dsc": dsc,
        }
        resp2 = self.client.post(url, data=post)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_double_submit_mismatch_blocks(self):
        """Mismatch between cookie and hidden token should block."""
        url = reverse("contact:contact")
        resp = self.client.get(url)
        ts, _dsc = self._get_tokens_from_response(resp)
        # Intentionally wrong token
        post = {
            "name": "Alice",
            "email": "alice@example.org",
            "message": "Valid message body that is long enough.",
            "website": "",
            "contact_ts": ts,
            "contact_dsc": "wrong",
        }
        resp2 = self.client.post(url, data=post)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_html_rejected_and_url_cap(self):
        """HTML content or too many URLs should be rejected."""
        url = reverse("contact:contact")
        resp = self.client.get(url)
        ts, dsc = self._get_tokens_from_response(resp)
        time.sleep(2)
        # HTML rejected
        post_html = {
            "name": "Alice",
            "email": "alice@example.org",
            "message": "<b>no html</b>",
            "suggestion": "on",
            "website": "",
            "contact_ts": ts,
            "contact_dsc": dsc,
        }
        resp_html = self.client.post(url, data=post_html)
        self.assertEqual(resp_html.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

        # URL cap
        content_many_urls = " ".join(
            [
                "https://a.example",
                "https://b.example",
                "https://c.example",
                "https://d.example",
            ]
        )
        post_urls = {
            "name": "Alice",
            "email": "alice@example.org",
            "message": content_many_urls,
            "suggestion": "on",
            "website": "",
            "contact_ts": ts,
            "contact_dsc": dsc,
        }
        resp_urls = self.client.post(url, data=post_urls)
        self.assertEqual(resp_urls.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_header_injection_prevention(self):
        """CR/LF in email should be rejected by form validator."""
        url = reverse("contact:contact")
        resp = self.client.get(url)
        ts, dsc = self._get_tokens_from_response(resp)
        time.sleep(2)
        post = {
            "name": "Alice",
            "email": "evil@example.org\nBcc: attacker@example.org",
            "message": "Valid message body that is long enough.",
            "suggestion": "on",
            "website": "",
            "contact_ts": ts,
            "contact_dsc": dsc,
        }
        resp2 = self.client.post(url, data=post)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_requires_at_least_one_category(self):
        """At least one category checkbox must be selected."""
        url = reverse("contact:contact")
        resp = self.client.get(url)
        ts, dsc = self._get_tokens_from_response(resp)
        time.sleep(2)
        post = {
            "name": "Alice",
            "email": "alice@example.org",
            "message": "Valid message body that is long enough.",
            # No category checked
            "website": "",
            "contact_ts": ts,
            "contact_dsc": dsc,
        }
        resp2 = self.client.post(url, data=post)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        resp2 = self.client.post(url, data=post)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
