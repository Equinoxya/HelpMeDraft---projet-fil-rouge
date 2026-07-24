from app import create_app
from app.extension import mail
from flask_mail import Message

app = create_app()

with app.app_context():
    print("MAIL_SERVER:", app.config.get("MAIL_SERVER"))
    print("MAIL_PORT:", app.config.get("MAIL_PORT"))
    print("MAIL_USERNAME:", repr(app.config.get("MAIL_USERNAME")))
    print("MAIL_PASSWORD:", repr(app.config.get("MAIL_PASSWORD")))
    print("MAIL_USE_TLS:", app.config.get("MAIL_USE_TLS"))
    print("MAIL_USE_SSL:", app.config.get("MAIL_USE_SSL"))

    msg = Message(
        subject="Test isolé",
        recipients=["test@example.com"],
        body="Ceci est un test",
    )
    mail.send(msg)
    print("ENVOI RÉUSSI !")