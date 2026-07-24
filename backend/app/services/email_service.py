from flask_mail import Message
from flask import current_app
import logging

def send_reset_password_email(mail, to_email: str, firstname:str, reset_link: str):
    msg = Message(
        subject="Réinitialisation de votre mot de passe - HelpMeDraft",
        recipients=[to_email],
        html=f"""
        <p>Bonjour {firstname},</p>
        <p>Vous avez demandé la réinitialisation de votre mot de passe.</p>
        <p><a href="{reset_link}">Cliquez ici pour choisir un nouveau mot de passe</a></p>
        <p>Ce lien est valable 1 heure. Si vous n'êtes pas à l'origine de cette demande, merci de nous contacter : contact@helpmedraft.com .</p>
        """
    )
    logging.basicConfig(level=logging.DEBUG)
    mail.send(msg)