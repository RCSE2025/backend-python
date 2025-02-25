import asyncio
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.core.config import settings

MAIL_PARAMS = {
    "TLS": settings.mail.TLS,
    "host": settings.mail.HOST,
    "password": settings.mail.MAIN_ADDRESS_PASSWORD,
    "user": settings.mail.MAIN_ADDRESS,
    "port": settings.mail.PORT,
}


async def send_mail_async(
    sender: str, to: list, subject: str, text: str, textType="plain", **params
):
    """Send an outgoing email with the given parameters.

    :param sender: From whom the email is being sent
    :type sender: str

    :param to: A list of recipient email addresses.
    :type to: list

    :param subject: The subject of the email.
    :type subject: str

    :param text: The text of the email.
    :type text: str

    :param textType: Mime subtype of text, defaults to 'plain' (can be 'html').
    :type text: str

    :param params: An optional set of parameters. (See below)
    :type params; dict

    Optional Parameters:
    :cc: A list of Cc email addresses.
    :bcc: A list of Bcc email addresses.
    """

    # Default Parameters
    cc = params.get("cc", [])
    bcc = params.get("bcc", [])
    mail_params = params.get("mail_params", MAIL_PARAMS)

    # Prepare Message
    msg = MIMEMultipart()
    # msg.preamble = subject.encode("utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = sender
    msg["To"] = ", ".join(to)
    if len(cc):
        msg["Cc"] = ", ".join(cc)
    if len(bcc):
        msg["Bcc"] = ", ".join(bcc)

    msg.attach(MIMEText(text, textType, "utf-8"))

    # Contact SMTP server and send Message
    host = mail_params.get("host", "localhost")
    isSSL = mail_params.get("SSL", False)
    isTLS = mail_params.get("TLS", False)
    if isSSL and isTLS:
        raise ValueError("SSL and TLS cannot both be True")
    port = mail_params.get("port", 465 if isSSL else 25)
    # For aiosmtplib 3.0.1 we must set argument start_tls=False
    # because we will explicitly be calling starttls ourselves when
    # isTLS is True:
    smtp = aiosmtplib.SMTP(hostname=host, port=port, start_tls=False, use_tls=isSSL)
    await smtp.connect()
    if isTLS:
        await smtp.starttls()
    if "user" in mail_params:
        await smtp.login(mail_params["user"], mail_params["password"])
    await smtp.send_message(msg)
    await smtp.quit()


async def test():
    co1 = send_mail_async(
        settings.mail.MAIN_ADDRESS,
        ["ivan.voronin.25@mail.ru"],
        "Test 1",
        "Test 1 Message",
        textType="plain",
    )
    co2 = send_mail_async(
        settings.mail.MAIN_ADDRESS,
        ["ivan.voronin.25@mail.ru"],
        "Test 2",
        "Test 2 Message",
        textType="plain",
    )
    co3 = send_mail_async(
        settings.mail.MAIN_ADDRESS,
        ["ivan.voronin.25@mail.ru"],
        "Test 3",
        "Test 3 Message",
        textType="plain",
    )

    await asyncio.gather(co1, co2, co3)


if __name__ == "__main__":
    asyncio.run(test())
