
from smtplib import SMTP
import  requests
import json
def send_alert_system(to_addrees,email_message):
    smtp = SMTP("smtppro.zoho.in", 587)
    smtp.starttls()

    smtp.login("kamlesh.bhati@cloudesign.com", "ftLET7VTygpd")

    smtp.sendmail("kamlesh.bhati@cloudesign.com", to_addrees, email_message)

    smtp.quit()

# try:
#     to_addrees = "bkamlesh213@gmail.com"
#     email_message = f"Subject: Alert System!\n\nCode Fat gaya"
#     send_alert_system(to_addrees,email_message)
# except Exception as exp:
#     print(exp)

