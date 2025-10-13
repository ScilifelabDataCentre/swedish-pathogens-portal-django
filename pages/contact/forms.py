from __future__ import annotations

"""Contact form definitions and anti-spam validation.

This module defines the `ContactForm` used by the contact page. It includes
layered, user-transparent anti-spam checks (honeypot, submission timing, and
double-submit cookie) and content validation.

The form accepts `request` in its constructor to access cookies for the
double-submit verification.
"""

import re
import time
from typing import Any, Optional

from django import forms
from django.core import signing
from django.core.exceptions import ValidationError


URL_REGEX = re.compile(r"(https?://|www\.)", re.IGNORECASE)

# Validation and anti-spam constants
MIN_SUBMIT_SECONDS = 2
MAX_TOKEN_AGE_SECONDS = 60 * 60
MAX_URLS_ALLOWED = 3


class ContactForm(forms.Form):
	"""Contact form with layered anti-spam.

	Fields:
		name: Optional full name of the sender (2–100 chars when provided).
		email: Optional reply address, validated when provided.
		message: Main text body, 20–5000 chars, with URL and HTML limits.
		suggestion, dm_support, other: Category checkboxes, at least one must
		    be selected.
		website: Honeypot field, must remain empty.
		contact_ts: Signed timestamp token to check submission timing.
		contact_dsc: Token that must match the cookie for double-submit check.

	Anti-spam strategy:
		- Honeypot rejects naive bots filling hidden fields.
		- TimestampSigner token rejects submissions that are too fast (<2s) or
		  too old (>60 minutes).
		- Double-submit cookie reduces scripted posts and replays.
	"""

	name = forms.CharField(min_length=2, max_length=100, required=False)
	email = forms.EmailField(required=False)
	message = forms.CharField(min_length=20, max_length=5000, widget=forms.Textarea)
	suggestion = forms.BooleanField(required=False)
	dm_support = forms.BooleanField(
		required=False, label="Request for data management/sharing support"
	)
	other = forms.BooleanField(required=False)

	# Anti-spam fields
	website = forms.CharField(required=False, widget=forms.HiddenInput)
	contact_ts = forms.CharField(widget=forms.HiddenInput, strip=False)
	contact_dsc = forms.CharField(widget=forms.HiddenInput, strip=False)

	# Internal state for logging (not exposed to users)
	_blocked_reason: Optional[str] = None

	def __init__(self, *args: Any, request=None, **kwargs: Any) -> None:
		"""Initialise the form.

		Args:
			*args: Positional form args.
			request: Optional HttpRequest to access cookies for token checks.
			**kwargs: Keyword form args.
		"""
		super().__init__(*args, **kwargs)
		self.request = request

	def clean_email(self) -> str:
		"""Validate email and prevent header injection.

		Returns:
			The sanitised email value.

		Raises:
			ValidationError: If CR/LF characters are present.
		"""
		value = self.cleaned_data.get("email", "")
		if "\r" in value or "\n" in value:
			raise ValidationError("Enter a valid email address.")
		return value

	def clean_message(self) -> str:
		"""Validate message content against HTML and URL constraints.

		Returns:
			The validated message content.

		Raises:
			ValidationError: If HTML-like tags are present or URL count exceeds
			    the allowed threshold.
		"""
		value = self.cleaned_data.get("message", "")
		# Reject HTML-like content
		if "<" in value or ">" in value:
			raise ValidationError("Please remove HTML tags.")
		# Cap URLs
		url_count = len(URL_REGEX.findall(value))
		if url_count > MAX_URLS_ALLOWED:
			raise ValidationError("Too many links in the message.")
		return value

	def clean(self) -> dict[str, Any]:
		"""Form-level validation for category, timing, and token checks.

		Returns:
			The cleaned data dictionary.

		Raises:
			ValidationError: On any anti-spam or category selection failure.
		"""
		cleaned = super().clean()

		# At least one category must be selected
		if not (
			cleaned.get("suggestion")
			or cleaned.get("dm_support")
			or cleaned.get("other")
		):
			raise ValidationError("Please select at least one option.")

		# Honeypot
		if cleaned.get("website"):
			self._blocked_reason = "HONEYPOT_HIT"
			raise ValidationError(
				"We couldn't submit the form. Please try again in a moment."
			)

		# Timing token
		ts_token = cleaned.get("contact_ts") or ""
		try:
			# Accept TimestampSigner style token or JSON payload signed via dumps
			try:
				signer = signing.TimestampSigner(salt="contact-ts")
				ts_str = signer.unsign(ts_token, max_age=MAX_TOKEN_AGE_SECONDS)
				ts = int(ts_str)
			except signing.BadSignature:
				payload = signing.loads(
					ts_token, salt="contact-ts", max_age=MAX_TOKEN_AGE_SECONDS
				)
				ts = int(payload.get("ts", 0))
		except signing.SignatureExpired:
			self._blocked_reason = "TOKEN_EXPIRED"
			raise ValidationError(
				"We couldn't submit the form. Please try again in a moment."
			)
		except signing.BadSignature:
			self._blocked_reason = "TOKEN_BAD_SIGNATURE"
			raise ValidationError(
				"We couldn't submit the form. Please try again in a moment."
			)

		now = int(time.time())
		if now - ts < MIN_SUBMIT_SECONDS:
			self._blocked_reason = "TOO_FAST"
			raise ValidationError(
				"We couldn't submit the form. Please try again in a moment."
			)

		# Double-submit cookie check
		posted_token = cleaned.get("contact_dsc") or ""
		cookie_token = None
		if hasattr(self, "request") and self.request is not None:
			cookie_token = self.request.COOKIES.get("contact_dsc")

		if not cookie_token or cookie_token != posted_token:
			self._blocked_reason = "TOKEN_MISMATCH"
			raise ValidationError(
				"We couldn't submit the form. Please try again in a moment."
			)

		return cleaned
