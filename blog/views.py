from django.shortcuts import render
from django.shortcuts import redirect

from django.contrib import messages

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from django.core.mail import send_mail
#send_mail('Subject here', 'Here is the message.', 'from@example.com', ['to@example.com'], fail_silently=False)

def contact_send_mail():
    my_subject = 'Subject here'
    my_message = 'Here is the message.'
    my_recipient = 'hellowordlabs@gmail.com'
    
    print("------------->", my_subject,"--", my_message,"--", my_recipient)
    
    
    
    send_mail(
        subject=my_subject,
        message=my_message,
        from_email='hellowordlabs@gmail.com',
        recipient_list=[my_recipient],
        fail_silently=False,
    )
        
def contact_send_mail2(request, subject, message, email):
    # # Collect required user input hardcode
    EMAIL_ADDRESS = "hellowordLabs@gmail.com"
    EMAIL_PASSWORD = "nvpgvhjafhcjmnxr"  # uses an app password
    EMAIL_DESTINATION = "hellowordLabs@gmail.com"
    EMAIL_SUBJECT = subject
    EMAIL_BODY = "Message from: "+email+"\nMessage:"+message

    # Create a MIMEText object to represent your email
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_DESTINATION
    msg['Subject'] = EMAIL_SUBJECT

    # Attach the body of the email to the MIMEText object
    msg.attach(MIMEText(EMAIL_BODY, 'plain'))
    # print("--------------------MIMEMultipart msg--------------------------")
    # print(msg)

    try:
        # Set up the SMTP client
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        # server.sendmail(EMAIL_ADDRESS, EMAIL_DESTINATION, msg.as_string())
        server.sendmail(EMAIL_ADDRESS, EMAIL_DESTINATION, msg.as_string())
        server.quit()
        print("Email sent successfully")
        messages.success(request, "Email sent successfully", extra_tags='alert')



    except Exception as e:
        print(f"Failed to send email: {e}")
        messages.error(request, "Failed to send email", extra_tags='alert-success')

