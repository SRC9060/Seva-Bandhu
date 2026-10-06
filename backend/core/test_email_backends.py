import base64
import json
import urllib.error
from io import BytesIO
from unittest.mock import MagicMock, patch

from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.test import SimpleTestCase, override_settings

from .email_backends import BrevoEmailBackend, BrevoEmailBackendError


BREVO_SETTINGS = {
    "BREVO_API_KEY": "test-brevo-api-key",
    "BREVO_SENDER_EMAIL": "verified@example.com",
    "BREVO_SENDER_NAME": "Seva Bandhu",
    "BREVO_API_TIMEOUT": 7,
    "DEFAULT_FROM_EMAIL": "verified@example.com",
}


def fake_api_response(status=201):
    response = MagicMock()
    response.status = status
    response.read.return_value = b'{"messageId":"test-message-id"}'
    context_manager = MagicMock()
    context_manager.__enter__.return_value = response
    context_manager.__exit__.return_value = False
    return context_manager


@override_settings(**BREVO_SETTINGS)
class BrevoEmailBackendTests(SimpleTestCase):
    @patch("core.email_backends.urllib.request.urlopen")
    def test_sends_plain_text_email_with_brevo_api_key_header(self, urlopen):
        urlopen.return_value = fake_api_response()
        message = EmailMessage(
            subject="Your verification code",
            body="Your code is 123456.",
            from_email="verified@example.com",
            to=["customer@example.com"],
        )

        sent = BrevoEmailBackend().send_messages([message])

        self.assertEqual(sent, 1)
        request = urlopen.call_args.args[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(request.full_url, "https://api.brevo.com/v3/smtp/email")
        self.assertEqual(request.get_header("Api-key"), "test-brevo-api-key")
        self.assertEqual(payload["sender"]["email"], "verified@example.com")
        self.assertEqual(payload["sender"]["name"], "Seva Bandhu")
        self.assertEqual(payload["to"], [{"email": "customer@example.com", "name": "customer"}])
        self.assertEqual(payload["textContent"], "Your code is 123456.")
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 7)

    @patch("core.email_backends.urllib.request.urlopen")
    def test_sends_html_invoice_attachment_as_base64(self, urlopen):
        urlopen.return_value = fake_api_response()
        message = EmailMultiAlternatives(
            subject="Your invoice",
            body="Your invoice is attached.",
            from_email="verified@example.com",
            to=["customer@example.com"],
        )
        message.attach_alternative("<p>Your invoice is attached.</p>", "text/html")
        message.attach("invoice_12.pdf", b"%PDF-test-content", "application/pdf")

        sent = BrevoEmailBackend().send_messages([message])

        self.assertEqual(sent, 1)
        payload = json.loads(urlopen.call_args.args[0].data.decode("utf-8"))
        self.assertEqual(payload["htmlContent"], "<p>Your invoice is attached.</p>")
        self.assertNotIn("textContent", payload)
        self.assertEqual(payload["attachment"][0]["name"], "invoice_12.pdf")
        self.assertEqual(
            base64.b64decode(payload["attachment"][0]["content"]),
            b"%PDF-test-content",
        )

    @override_settings(BREVO_API_KEY="")
    def test_missing_api_key_fails_with_actionable_error(self):
        message = EmailMessage(
            subject="OTP",
            body="123456",
            from_email="verified@example.com",
            to=["customer@example.com"],
        )
        with self.assertRaisesMessage(ImproperlyConfigured, "BREVO_API_KEY"):
            BrevoEmailBackend().send_messages([message])

    @patch("core.email_backends.urllib.request.urlopen")
    def test_brevo_http_error_does_not_report_success(self, urlopen):
        urlopen.side_effect = urllib.error.HTTPError(
            "https://api.brevo.com/v3/smtp/email",
            401,
            "Unauthorized",
            hdrs=None,
            fp=BytesIO(b'{"message":"Invalid API key"}'),
        )
        message = EmailMessage(
            subject="OTP",
            body="123456",
            from_email="verified@example.com",
            to=["customer@example.com"],
        )
        with self.assertRaisesRegex(BrevoEmailBackendError, "HTTP 401"):
            BrevoEmailBackend().send_messages([message])
