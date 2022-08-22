import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import hashlib
import datetime


def generate_code(email):
    now = datetime.datetime.now().__str__()
    int(hashlib.sha1(email.encode("utf-8")).hexdigest(), 16)
    return abs(hash(email+now)) % (10 ** 5)


def send(email, code, chat_id):
    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    sender_email = "s21checkin@gmail.com"
    password = "lcjamekoxrhyxxov"
    message = MIMEMultipart("alternative")
    message["Subject"] = "Registration on 21 School Checkin Bot"
    message["From"] = sender_email
    message["To"] = email

    # Create the plain-text and HTML version of your message
    html = """\
    <html>
      <body>
        <p>Привет!,<br>
           Вот твой код доступа к боту:<br>
           <h1>{0}</h1>
        </p>
      </body>
    </html>
    """
    html = html.format(code, chat_id)
    part2 = MIMEText(html, "html")
    message.attach(part2)

    # Create a secure SSL context
    context = ssl.create_default_context()

    try:
        server = smtplib.SMTP(smtp_server,port)
        # server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        # server.ehlo() # Can be omitted
        server.login(sender_email, password)
        server.sendmail(sender_email, email, message.as_string())
    except Exception as e:
        print(e)
    finally:
        server.quit()
