import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import base64
from io import BytesIO
from PIL import Image

# Step 1: Prepare the image
image = Image.open('path_to_your_image.jpg')
buffered = BytesIO()
image.save(buffered, format="PNG")
image_encoded = base64.b64encode(buffered.getvalue()).decode()

# Step 2: Create the email message
msg = MIMEMultipart('related')
msg['From'] = 'your_email@example.com'
msg['To'] = 'recipient@example.com'
msg['Subject'] = 'Email with Embedded Image'

# Plain text part
text = MIMEText('This is an important message with an embedded image.', 'plain')
msg.attach(text)

# HTML part
html = f"""
<html>
  <head></head>
  <body>
    <p>This is an important message with an embedded image:</p>
    <img src="data:image/png;base64,{image_encoded}">
  </body>
</html>
"""
html_part = MIMEText(html, 'html')
msg.attach(html_part)

# Step 3: Send the email
with smtplib.SMTP('smtp.example.com', 587) as server:
    server.starttls()
    server.login('your_email@example.com', 'your_password')
    server.sendmail('your_email@example.com', 'recipient@example.com', msg.as_string())

print("Email sent successfully!")
