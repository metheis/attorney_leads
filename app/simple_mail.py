# email.py

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from starlette.responses import JSONResponse
from email_validator import validate_email, EmailNotValidError

def val_address(email):
    try:
        valid = validate_email(email)
        return True
    except EmailNotValidError as e:
        return False

conf = ConnectionConfig(
    MAIL_USERNAME = "smtp server username",
    MAIL_PASSWORD = "smtp server password",
    MAIL_FROM = "system@company.com",
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.company.com",
    MAIL_FROM_NAME="Candidate Management System",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def simple_send_candidate(email: str, full_name: str) -> JSONResponse:
    html = f"""<p>Hi {full_name}, thanks for submitted the form!</p> """

    if (not val_address(email)):
        return JSONResponse(status_code=400, content={"message": "Invalid email address"})
    
    return JSONResponse(status_code=200, content={"message": "email would be sent"})

    message = MessageSchema(
        subject="Form Confirmation",
        recipients=[email],
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})

async def simple_send_attorney(email: str, att_full_name: str,  cand_full_name: str) -> JSONResponse:
    html = f"""<p>Hi {att_full_name}, {cand_full_name} has just submitted the form!</p> """

    if (not val_address(email)):
        return JSONResponse(status_code=400, content={"message": "Invalid email address"})
    
    return JSONResponse(status_code=200, content={"message": "email would be sent"})

    message = MessageSchema(
        subject="Form Submitted Notification",
        recipients=[email],
        body=html,
        subtype=MessageType.html)

    fm = FastMail(conf)
    await fm.send_message(message)
    return JSONResponse(status_code=200, content={"message": "email has been sent"})
