"""Módulo de envio de alertas por e-mail."""

import smtplib
from email.message import EmailMessage
import streamlit as st

def enviar_alerta_email(destinatario: str, assunto: str, corpo: str):
    """Dispara e-mail de alerta usando credenciais SMTP configuradas nos secrets do Streamlit."""
    try:
        # Configurações obtidas do st.secrets do Streamlit para segurança
        smtp_server = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = st.secrets.get("SMTP_PORT", 587)
        remetente = st.secrets.get("SMTP_EMAIL", "seu-email@gmail.com")
        senha = st.secrets.get("SMTP_PASSWORD", "sua-senha-de-app")

        msg = EmailMessage()
        msg.set_content(corpo)
        msg["Subject"] = assunto
        msg["From"] = remetente
        msg["To"] = destinatario

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(remetente, senha)
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False