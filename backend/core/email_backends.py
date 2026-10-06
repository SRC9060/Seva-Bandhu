"""Django email backend that sends transactional messages through Brevo's HTTPS API.

Use this backend for OTPs, invoices (including PDF attachments), and other Django
EmailMessage/send_mail calls. It avoids SMTP ports, which are blocked on Render's
free web services.
"""
import base64
import json
import logging
import urllib.error
import urllib.request
from email.mime.base import MIMEBase
from email.utils import parseaddr

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.backends.base import BaseEmailBackend

logger = logging.getLogger(__name__)

BREVO_SEND_EMAIL_URL = "https://api.brevo.com/v3/smtp/email"


class BrevoEmailBackendError(RuntimeError):
    """Raised when Brevo rejects an email or cannot be reached."""


class BrevoEmailBackend(BaseEmailBackend):
    """Send Django email messages using Brevo's transactional email API."""

    def __init__(self, fail_silently=False, api_key=None, timeout=None, **kwargs):
        super().__init__(fail_silently=fail_silently)
        self.api_key = api_key if api_key is not None else getattr(settings, "BREVO_API_KEY", "")
        self.timeout = timeout if timeout is not None else getattr(settings, "BREVO_API_TIMEOUT", 15)

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        if not self.api_key:
            error = ImproperlyConfigured(
                "Brevo email is selected but BREVO_API_KEY is not configured."
            )
            if self.fail_silently:
                logger.error("%s", error)
                return 0
            raise error

        sent = 0
        for message in email_messages:
            try:
                self._send(message)
            except Exception:
                if not self.fail_silently:
                    raise
                logger.exception("Brevo failed to send a transactional email.")
            else:
                sent += 1
        return sent

    @staticmethod
    def _address_object(raw_address, *, default_name=""):
        name, address = parseaddr(raw_address or "")
        address = address.strip()
        if not address or "@" not in address:
            raise ImproperlyConfigured(
                "Configure a valid sender/recipient email address for Brevo."
            )
        # Brevo rejects recipients whose name is missing/empty ("name is missing in to").
        # Django commonly supplies plain addresses with no display name; derive a
        # deterministic non-empty fallback from the address's local part.
        display_name = name.strip() or default_name.strip() or address.split("@", 1)[0].strip() or "Recipient"
        return {"email": address, "name": display_name}

    @staticmethod
    def _recipient_list(addresses):
        return [
            BrevoEmailBackend._address_object(address)
            for address in (addresses or [])
            if address
        ]

    @staticmethod
    def _attachment_object(attachment):
        if isinstance(attachment, MIMEBase):
            filename = attachment.get_filename() or "attachment"
            content = attachment.get_payload(decode=True)
            if content is None:
                raw_content = attachment.get_payload()
                content = raw_content.encode("utf-8") if isinstance(raw_content, str) else bytes(raw_content)
        elif isinstance(attachment, (tuple, list)) and len(attachment) >= 2:
            filename = attachment[0] or "attachment"
            content = attachment[1]
            if content is None:
                content = b""
            elif isinstance(content, str):
                content = content.encode(getattr(settings, "DEFAULT_CHARSET", "utf-8"))
            elif not isinstance(content, bytes):
                content = bytes(content)
        else:
            raise TypeError("Unsupported Django email attachment type.")

        return {
            "name": str(filename),
            "content": base64.b64encode(content).decode("ascii"),
        }

    @staticmethod
    def _alternative_parts(message):
        html_content = message.body if getattr(message, "content_subtype", "plain") == "html" else None

        for alternative in getattr(message, "alternatives", []) or []:
            if isinstance(alternative, (tuple, list)) and len(alternative) >= 2:
                content, mimetype = alternative[0], alternative[1]
            else:
                content = getattr(alternative, "content", "")
                mimetype = getattr(alternative, "mimetype", "")

            if mimetype == "text/html":
                html_content = content
        return html_content

    def _build_payload(self, message):
        configured_sender = getattr(settings, "BREVO_SENDER_EMAIL", "").strip()
        fallback_from = getattr(message, "from_email", None) or getattr(settings, "DEFAULT_FROM_EMAIL", "")
        sender_source = configured_sender or fallback_from
        sender_name, sender_email = parseaddr(sender_source or "")
        if not sender_email and "@" in (sender_source or ""):
            sender_email = sender_source.strip()
        if not sender_email or "@" not in sender_email:
            raise ImproperlyConfigured(
                "Set BREVO_SENDER_EMAIL to an email address verified in Brevo."
            )

        configured_name = getattr(settings, "BREVO_SENDER_NAME", "").strip()
        sender = {
            "email": sender_email,
            "name": configured_name or sender_name or "Seva Bandhu",
        }

        recipients = self._recipient_list(getattr(message, "to", []))
        if not recipients:
            raise ValueError("Cannot send a Brevo email without at least one To recipient.")

        payload = {
            "sender": sender,
            "to": recipients,
            "subject": message.subject or "Seva Bandhu notification",
        }

        cc = self._recipient_list(getattr(message, "cc", []))
        bcc = self._recipient_list(getattr(message, "bcc", []))
        if cc:
            payload["cc"] = cc
        if bcc:
            payload["bcc"] = bcc

        html_content = self._alternative_parts(message)
        if html_content is not None:
            payload["htmlContent"] = html_content
        else:
            payload["textContent"] = message.body or ""

        reply_to = getattr(message, "reply_to", None) or []
        if reply_to:
            payload["replyTo"] = self._address_object(reply_to[0])

        attachments = [
            self._attachment_object(attachment)
            for attachment in (getattr(message, "attachments", []) or [])
        ]
        if attachments:
            payload["attachment"] = attachments

        # Only forward custom X-* headers. Standard MIME headers are managed by Brevo.
        extra_headers = getattr(message, "extra_headers", {}) or {}
        custom_headers = {
            str(key): str(value)
            for key, value in extra_headers.items()
            if str(key).lower().startswith("x-")
        }
        if custom_headers:
            payload["headers"] = custom_headers

        return payload

    def _send(self, message):
        payload = self._build_payload(message)
        request = urllib.request.Request(
            BREVO_SEND_EMAIL_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "accept": "application/json",
                "api-key": self.api_key,
                "content-type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                status_code = getattr(response, "status", 200)
                if not 200 <= status_code < 300:
                    raise BrevoEmailBackendError(
                        f"Brevo email API returned HTTP {status_code}."
                    )
                # Brevo returns a messageId for accepted messages. Acceptance is
                # not a guarantee that the recipient's mailbox has delivered it.
                response.read()
                return True
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            detail = detail[:500] if detail else "No error details returned."
            raise BrevoEmailBackendError(
                f"Brevo rejected the email (HTTP {error.code}): {detail}"
            ) from None
        except urllib.error.URLError as error:
            reason = str(getattr(error, "reason", "network error"))
            raise BrevoEmailBackendError(
                f"Could not reach Brevo's email API: {reason}"
            ) from None
        except TimeoutError:
            raise BrevoEmailBackendError("Brevo's email API request timed out.") from None
