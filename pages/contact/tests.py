"""Tests for the contact form and view.

Covers anti-spam (honeypot, timing, token), validation, and email sending.
Uses Django's locmem email backend for assertions.

TODO: adapt depending on the test tooling chosen (TestCase, Pytest).
"""

from __future__ import annotations

import re
import time
from unittest.mock import MagicMock, patch

from django.core import mail, signing
from django.http import HttpResponse
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .forms import CONTACT_TS_SIGNER, MAX_URLS_ALLOWED, MIN_SUBMIT_SECONDS


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    DEFAULT_FROM_EMAIL="Pathogens Portal <no-reply@example.org>",
)
class ContactFormTests(TestCase):
    """Integration tests for the contact view and form."""

    def setUp(self) -> None:
        """Initialise test client for each test."""
        self.client = Client()
        self.url = reverse("contact:contact")

    def _get_tokens_from_response(self, response: HttpResponse) -> tuple[str | None, str | None]:
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

    def _get_fresh_tokens(self) -> tuple[str, str]:
        """Perform a GET and return non-empty anti-spam tokens.

        Encapsulates the common "GET + parse hidden fields" pattern while
        ensuring failures are reported with a clear assertion message.
        """
        resp = self.client.get(self.url)
        ts, dsc = self._get_tokens_from_response(resp)
        if ts is None or dsc is None:
            self.fail("Contact form did not render anti-spam tokens.")
        return ts, dsc

    def _age_timestamp_token(self, _ts_token: str) -> str:
        """Return a timestamp token old enough to satisfy the minimum delay.

        This avoids using time.sleep() in tests by re-signing a value that
        represents a time sufficiently in the past for the ContactForm timing
        check, while keeping the double-submit cookie unchanged.
        """
        now = int(time.time())
        aged_value = str(now - (MIN_SUBMIT_SECONDS + 1))
        return CONTACT_TS_SIGNER.sign(aged_value)

    def _build_post_data(self, ts: str, dsc: str, **overrides) -> dict[str, str | list[str]]:
        """Return a baseline valid payload merged with overrides."""
        data = {
            "name": "Alice",
            "email": "alice@example.org",
            "message": "This is a valid message body that is long enough.",
            "category": ["suggestion"],
            "website": "",
            "contact_ts": ts,
            "contact_dsc": dsc,
        }
        data.update(overrides)
        return data

    def test_get_renders_form_and_sets_cookie(self):
        """GET should render the form and set the double-submit cookie."""
        resp = self.client.get(self.url)
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
        # No CSRF token provided on POST
        resp = client.post(self.url, data={})
        self.assertEqual(resp.status_code, 403)

    def test_happy_path_sends_email(self):
        """Valid submission sends a single email with expected subject."""
        ts, dsc = self._get_fresh_tokens()
        ts = self._age_timestamp_token(ts)
        post = self._build_post_data(ts, dsc)
        resp2 = self.client.post(self.url, data=post, follow=True)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual("[Contact] Contact and suggestions form", mail.outbox[0].subject)
        # Success message present after redirect
        self.assertIn(b"Thanks! Your message was sent", resp2.content)

    def test_honeypot_blocks(self):
        """Filling the honeypot field must block submission and log a reason."""
        ts, dsc = self._get_fresh_tokens()
        post = self._build_post_data(ts, dsc, website="spam")
        with self.assertLogs("pages.contact.views", level="WARNING") as cm:
            resp2 = self.client.post(self.url, data=post)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(
            any("reason=HONEYPOT_HIT" in message for message in cm.output),
            cm.output,
        )

    def test_timing_too_fast_blocks(self):
        """Posting faster than 2s after GET should be blocked and logged."""
        ts, dsc = self._get_fresh_tokens()
        post = self._build_post_data(ts, dsc)
        with self.assertLogs("pages.contact.views", level="WARNING") as cm:
            resp2 = self.client.post(self.url, data=post)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(
            any("reason=TOO_FAST" in message for message in cm.output),
            cm.output,
        )

    @patch("pages.contact.views.EmailMessage.send", side_effect=Exception("SMTP down"))
    def test_smtp_failure_path(self, _mock_send: MagicMock):
        """If SMTP fails, log and display a generic error, and do not send email."""
        ts, dsc = self._get_fresh_tokens()
        ts = self._age_timestamp_token(ts)
        post = self._build_post_data(ts, dsc)
        with self.assertLogs("pages.contact.views", level="WARNING") as cm:
            resp2 = self.client.post(self.url, data=post)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        # Generic error summary presented to the user
        self.assertIn(
            b"We couldn't submit the form. Please check the fields below.",
            resp2.content,
        )
        # Tokens refreshed and cookie matches hidden field
        ts2, dsc2 = self._get_tokens_from_response(resp2)
        self.assertIsNotNone(ts2)
        self.assertIsNotNone(dsc2)
        cookie_dsc = self.client.cookies.get("contact_dsc").value
        self.assertEqual(dsc2, cookie_dsc)
        # Logs for email send error and blocked outcome
        self.assertTrue(
            any("outcome=error reason=EMAIL_SEND_ERROR" in m for m in cm.output),
            cm.output,
        )
        self.assertTrue(
            any("outcome=blocked reason=EMAIL_SEND_ERROR" in m for m in cm.output),
            cm.output,
        )

    def test_double_submit_mismatch_blocks(self):
        """Mismatch between cookie and hidden token should block and be logged."""
        ts, _dsc = self._get_fresh_tokens()
        # Intentionally wrong token
        post = self._build_post_data(ts, "wrong")
        with self.assertLogs("pages.contact.views", level="WARNING") as cm:
            resp2 = self.client.post(self.url, data=post)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        # Category hint should not appear for non-category errors
        self.assertNotIn(b"Please select at least one alternative.", resp2.content)
        self.assertTrue(
            any("reason=TOKEN_MISMATCH" in message for message in cm.output),
            cm.output,
        )

    def test_html_rejected_and_url_cap(self):
        """HTML content or too many URLs should be rejected."""
        ts, dsc = self._get_fresh_tokens()
        ts = self._age_timestamp_token(ts)
        # HTML rejected
        post_html = self._build_post_data(ts, dsc, message="<b>no html</b>")
        resp_html = self.client.post(self.url, data=post_html)
        self.assertEqual(resp_html.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

        # URL cap
        content_many_urls = " ".join([f"https://{i}.example" for i in range(MAX_URLS_ALLOWED + 1)])
        post_urls = self._build_post_data(ts, dsc, message=content_many_urls)
        resp_urls = self.client.post(self.url, data=post_urls)
        self.assertEqual(resp_urls.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_header_injection_prevention(self):
        """CR/LF in email should be rejected by form validator."""
        ts, dsc = self._get_fresh_tokens()
        ts = self._age_timestamp_token(ts)
        post = self._build_post_data(
            ts,
            dsc,
            email="evil@example.org\nBcc: attacker@example.org",
        )
        resp2 = self.client.post(self.url, data=post)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        # Field-level error should be shown
        self.assertIn(b"Enter a valid email address.", resp2.content)

    def test_message_too_short_shows_error_and_no_email(self):
        """Message shorter than 20 chars should raise a field error."""
        ts, dsc = self._get_fresh_tokens()
        ts = self._age_timestamp_token(ts)
        post = self._build_post_data(ts, dsc, message="too short")
        with self.assertLogs("pages.contact.views", level="WARNING") as cm:
            resp = self.client.post(self.url, data=post)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn(b"at least 20 characters", resp.content)
        self.assertTrue(
            any("reason=VALIDATION_ERROR" in message for message in cm.output),
            cm.output,
        )

    def test_message_just_over_max_length_shows_error_and_no_email(self):
        """Message longer than the max length should raise a field error."""
        ts, dsc = self._get_fresh_tokens()
        ts = self._age_timestamp_token(ts)
        long_message = "x" * 5001
        post = self._build_post_data(ts, dsc, message=long_message)
        resp = self.client.post(self.url, data=post)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn(b"at most 5000 characters", resp.content)

    def test_requires_at_least_one_category(self):
        """At least one category checkbox must be selected and error shown."""
        ts, dsc = self._get_fresh_tokens()
        ts = self._age_timestamp_token(ts)
        post = self._build_post_data(ts, dsc)
        post.pop("category")
        with self.assertLogs("pages.contact.views", level="WARNING") as cm:
            resp2 = self.client.post(self.url, data=post)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        # Custom category error message from the form
        self.assertIn(b"Please select at least one alternative.", resp2.content)
        self.assertTrue(
            any("reason=VALIDATION_ERROR" in message for message in cm.output),
            cm.output,
        )

    def test_missing_cookie_blocks_with_token_mismatch_reason(self):
        """If the cookie is missing but hidden token is present, treat as token mismatch."""
        ts, dsc = self._get_fresh_tokens()
        # Remove the cookie before POST
        if "contact_dsc" in self.client.cookies:
            del self.client.cookies["contact_dsc"]
        post = self._build_post_data(ts, dsc)
        with self.assertLogs("pages.contact.views", level="WARNING") as cm:
            resp = self.client.post(self.url, data=post)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(
            any("reason=TOKEN_MISMATCH" in message for message in cm.output),
            cm.output,
        )

    def test_missing_hidden_token_blocks_with_token_mismatch_reason(self):
        """If the hidden token is missing but cookie is present, treat as token mismatch."""
        ts, dsc = self._get_fresh_tokens()
        post = self._build_post_data(ts, dsc)
        post.pop("contact_dsc")
        with self.assertLogs("pages.contact.views", level="WARNING") as cm:
            resp = self.client.post(self.url, data=post)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(
            any("reason=TOKEN_MISMATCH" in message for message in cm.output),
            cm.output,
        )

    def test_invalid_timestamp_token_blocks_with_bad_signature_reason(self):
        """An invalid timestamp token should be treated as a bad signature."""
        ts, dsc = self._get_fresh_tokens()
        bad_ts = "invalid-token-payload"
        post = self._build_post_data(bad_ts, dsc)
        with self.assertLogs("pages.contact.views", level="WARNING") as cm:
            resp = self.client.post(self.url, data=post)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(
            any("reason=TOKEN_BAD_SIGNATURE" in message for message in cm.output),
            cm.output,
        )

    @patch(
        "pages.contact.forms.CONTACT_TS_SIGNER.unsign",
        side_effect=signing.SignatureExpired("expired"),
    )
    def test_expired_timestamp_token_blocks_with_bad_signature_reason(
        self, _mock_unsign: MagicMock
    ):
        """An expired timestamp token should be treated as a bad signature."""
        ts, dsc = self._get_fresh_tokens()
        post = self._build_post_data(ts, dsc)
        with self.assertLogs("pages.contact.views", level="WARNING") as cm:
            resp = self.client.post(self.url, data=post)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(
            any("reason=TOKEN_BAD_SIGNATURE" in message for message in cm.output),
            cm.output,
        )

    def test_resubmission_after_error_works_without_reload(self):
        """After validation error, new tokens/cookie allow retry without page reload."""
        # Initial GET
        resp = self.client.get(self.url)
        ts1, dsc1 = self._get_tokens_from_response(resp)
        # Trigger a validation error (e.g., message too short)
        post_invalid = self._build_post_data(ts1, dsc1, message="short")
        resp_invalid = self.client.post(self.url, data=post_invalid)
        self.assertEqual(resp_invalid.status_code, 200)
        # Extract refreshed tokens from the error page
        ts2, dsc2 = self._get_tokens_from_response(resp_invalid)
        # Cookie must match hidden token
        cookie_dsc = self.client.cookies.get("contact_dsc").value
        self.assertEqual(dsc2, cookie_dsc)
        # Retry with corrected message and refreshed tokens using an "aged" token
        ts2 = self._age_timestamp_token(ts2)
        post_valid = self._build_post_data(ts2, dsc2)
        resp_valid = self.client.post(self.url, data=post_valid, follow=True)
        self.assertEqual(resp_valid.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)

    def test_email_required_shows_error_and_blocks_send(self):
        """Blank email must raise a validation error and not send mail."""
        ts, dsc = self._get_fresh_tokens()
        ts = self._age_timestamp_token(ts)
        post = self._build_post_data(ts, dsc, email="")
        resp = self.client.post(self.url, data=post)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn(b"This field is required.", resp.content)

    def test_name_required_shows_error_and_blocks_send(self):
        """Blank name must raise a validation error and not send mail."""
        ts, dsc = self._get_fresh_tokens()
        ts = self._age_timestamp_token(ts)
        post = self._build_post_data(ts, dsc, name="")
        resp = self.client.post(self.url, data=post)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn(b"This field is required.", resp.content)

    def test_message_html_error_message_is_user_friendly(self):
        """HTML-like content should trigger a clear validation error message."""
        ts, dsc = self._get_fresh_tokens()
        ts = self._age_timestamp_token(ts)
        message_with_html = "<b>" + "this message contains html tags" + "</b>"
        post = self._build_post_data(ts, dsc, message=message_with_html)
        resp = self.client.post(self.url, data=post)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertIn(b"Please remove HTML tags.", resp.content)

    def test_category_invalid_choice_rejected(self):
        """An invalid category choice should be rejected as a validation error."""
        ts, dsc = self._get_fresh_tokens()
        ts = self._age_timestamp_token(ts)
        post = self._build_post_data(ts, dsc, category=["not-a-valid-choice"])
        with self.assertLogs("pages.contact.views", level="WARNING") as cm:
            resp = self.client.post(self.url, data=post)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertTrue(
            any("reason=VALIDATION_ERROR" in message for message in cm.output),
            cm.output,
        )

    def test_cookie_secure_flag_respects_https_request(self):
        """When accessed over HTTPS, the contact cookie should be marked secure."""
        resp = self.client.get(self.url, secure=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("contact_dsc", resp.cookies)
        self.assertTrue(resp.cookies["contact_dsc"]["secure"])
        self.assertTrue(resp.cookies["contact_dsc"]["httponly"])

    def test_tokens_regenerated_on_each_get(self):
        """Each GET should issue fresh anti-spam tokens."""
        resp1 = self.client.get(self.url)
        ts1, dsc1 = self._get_tokens_from_response(resp1)
        resp2 = self.client.get(self.url)
        ts2, dsc2 = self._get_tokens_from_response(resp2)
        self.assertNotEqual(dsc1, dsc2)
