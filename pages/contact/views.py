"""Views for the contact page.

This module contains a `FormView`-based implementation that issues anti-spam
tokens on GET and validates user input on POST before sending an email via
Django's email backend.
"""

from __future__ import annotations

import logging
import os
import secrets
import time
from typing import Any

from django.conf import settings
from django.core import signing
from django.core.mail import EmailMessage
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from django.contrib import messages

from .forms import ContactForm


class Contact(FormView):
    template_name = "contact/contact_form.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact:contact")
    title = "Contact and suggestions form"
    logger = logging.getLogger(__name__)

    def get_form_kwargs(self) -> dict[str, Any]:
        """Inject request into the form for cookie access.

        Returns:
            Keyword arguments for form construction including `request`.
        """
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def _generate_tokens(self) -> tuple[str, str]:
        """Create a signed timestamp token and a double-submit cookie value.

        Returns:
            A tuple ``(signed_ts, dsc_token)`` where ``signed_ts`` is produced
            by `TimestampSigner` and ``dsc_token`` is a random string.
        """
        signer = signing.TimestampSigner(salt="contact-ts")
        signed_ts = signer.sign(str(int(time.time())))
        dsc_token = secrets.token_urlsafe(16)
        return signed_ts, dsc_token

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Render the form and set anti-spam tokens/cookie.

        Sets the signed timestamp and double-submit token as hidden fields and
        sets a HttpOnly cookie (`contact_dsc`).
        """
        form = self.get_form()
        signed_ts, dsc_token = self._generate_tokens()
        form.initial.update(
            {
                "contact_ts": signed_ts,
                "contact_dsc": dsc_token,
            }
        )

        response = self.render_to_response(self.get_context_data(form=form))
        # HttpOnly cookie, secure flag will be added by Django when using HTTPS in prod
        secure_flag = (
            self.request.is_secure()
            if hasattr(self.request, "is_secure")
            else getattr(settings, "SESSION_COOKIE_SECURE", False)
        )

        response.set_cookie(
            key="contact_dsc",
            value=dsc_token,
            max_age=30 * 60,
            httponly=True,
            secure=secure_flag,
            samesite=getattr(settings, "SESSION_COOKIE_SAMESITE", "Lax"),
        )
        return response

    def form_valid(self, form: ContactForm) -> HttpResponse:
        """Compose and send the email, then redirect.

        Builds a plain-text body including name, email, selected categories and
        origin URL. Adds `Reply-To` only if the user provided an email.
        """
        from_email = getattr(
            settings,
            "DEFAULT_FROM_EMAIL",
            os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@example.org"),
        )
        recipient = getattr(
            settings,
            "CONTACT_RECIPIENT_EMAIL",
            os.environ.get("CONTACT_RECIPIENT_EMAIL", "dev-null@example.org"),
        )

        name = form.cleaned_data.get("name", "")
        user_email = form.cleaned_data.get("email", "")
        message = form.cleaned_data["message"]

        # Build category summary mirroring old portal
        categories = []
        if form.cleaned_data.get("suggestion"):
            categories.append("Suggestion for the Portal")
        if form.cleaned_data.get("dm_support"):
            categories.append("Request for data management or data sharing support")
        if form.cleaned_data.get("other"):
            categories.append("Other")
        origin_url = self.request.build_absolute_uri(self.request.path)

        body = (
            f"From: {name}\n"
            f"Email: {user_email}\n"
            f"Categories: {', '.join(categories) if categories else '—'}\n"
            f"Origin URL: {origin_url}\n\n"
            f"{message}"
        )

        start = time.time()
        try:
            headers = {"Reply-To": user_email} if user_email else None
            email = EmailMessage(
                subject="[Contact] Contact and suggestions form",
                body=body,
                from_email=from_email,
                to=[recipient],
                headers=headers,
            )
            email.send(fail_silently=False)
            duration_ms = int((time.time() - start) * 1000)
            self.logger.info(
                "event=contact_submit outcome=success duration_ms=%s", duration_ms
            )
            messages.success(
                self.request,
                "Thanks! Your message was sent, we’ll get back to you soon.",
            )
        except Exception:  # noqa: BLE001
            duration_ms = int((time.time() - start) * 1000)
            self.logger.error(
                "event=contact_submit outcome=error reason=EMAIL_SEND_ERROR duration_ms=%s",
                duration_ms,
                exc_info=True,
            )
            # Re-render the form with a generic error
            form.add_error(
                None, "We couldn't submit the form. Please try again in a moment."
            )
            return self.form_invalid(form)

        # Redirect to clear POST and show success state
        return super().form_valid(form)

    def form_invalid(self, form: ContactForm) -> HttpResponse:
        """Log a reason code without personal information and re-render the form."""
        reason = getattr(form, "_blocked_reason", None) or "VALIDATION_ERROR"
        self.logger.warning(
            "event=contact_submit outcome=blocked reason=%s", reason
        )
        # Re-issue tokens and cookie so user can retry without reload
        signed_ts, dsc_token = self._generate_tokens()
        # Update both initial and bound data so rendered hidden inputs match the new cookie
        form.fields["contact_ts"].initial = signed_ts
        form.fields["contact_dsc"].initial = dsc_token
        try:
            data = form.data.copy()
            data["contact_ts"] = signed_ts
            data["contact_dsc"] = dsc_token
            form.data = data
        except Exception:  # noqa: BLE001
            # If form.data is not a QueryDict (unlikely), continue with initial values only
            pass
        response = super().form_invalid(form)
        secure_flag = (
            self.request.is_secure()
            if hasattr(self.request, "is_secure")
            else getattr(settings, "SESSION_COOKIE_SECURE", False)
        )
        response.set_cookie(
            key="contact_dsc",
            value=dsc_token,
            max_age=30 * 60,
            httponly=True,
            secure=secure_flag,
            samesite=getattr(settings, "SESSION_COOKIE_SAMESITE", "Lax"),
        )
        return response
