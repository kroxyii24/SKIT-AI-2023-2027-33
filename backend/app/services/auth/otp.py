import hashlib
import secrets
import smtplib
from email.message import EmailMessage

from app.core.config import settings


def generate_otp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()


def send_otp_email(email: str, otp: str) -> None:
    message = EmailMessage()

    message["Subject"] = "JanSwasthya AI - Email Verification"
    message["From"] = settings.SMTP_FROM
    message["To"] = email

    message.set_content(
        f"""
Hello,

Welcome to JanSwasthya AI.

Your email verification OTP is:

{otp}

This OTP is valid for 5 minutes.

If you did not request this verification, please ignore this email.

Regards,
JanSwasthya AI Team
"""
    )

    with smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT,
    ) as server:
        server.starttls()

        server.login(
            settings.SMTP_USERNAME,
            settings.SMTP_PASSWORD,
        )

        server.send_message(message)