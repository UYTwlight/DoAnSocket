import socket
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.message import EmailMessage
from email.utils import make_msgid
import os
from email.utils import formatdate
import mimetypes
import locale
import json
import re


# Đọc thông tin file json
file_path="./config.json"
with open(file_path, 'r') as file:
    data = json.load(file)

# # Thông tin server
# PORT = data["General"]["MailServer"]
# POP3_SERVER = data["General"]["POP3"]


# Thông tin máy chủ và cổng
mail_from = data["General"]["Username"]
result = re.search(r'<(.*)>', mail_from)
if result:
    mail_from = result.group(1)
smtp_server = data["General"]["MailServer"]
smtp_port = data["General"]["SMTP"]

def SEND_MAIL(client_socket):

    # Tạo kết nối socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((smtp_server, smtp_port))

        # Gửi lệnh EHLO để bắt đầu phiên làm việc
    ehlo_command=f"EHLO [{smtp_server}]\r\n"
    client_socket.sendall(ehlo_command.encode())
    response = client_socket.recv(1024).decode()
    #print(response)
    # Gửi mail form
    # mail_from=input("MAIL FROM: " )
    client_socket.sendall(f"MAIL FROM:<{mail_from}>\r\n".encode())
    response = client_socket.recv(1024).decode()
    #print(response)
    # Gửi RPCT
    recipient_mail=input("To: ")
    recipient_mails=[]
    recipient_mails = [email.strip() for email in recipient_mail.split(',') if email.strip()]
    # print(recipient_mails)
    for i in recipient_mails:
        client_socket.sendall(f"RCPT TO: <{i}>\r\n".encode())
        response = client_socket.recv(1024).decode()
    # print(response)
    cc_mail=input("CC: ")
    if cc_mail!='':
        cc_mails=[]
        cc_mails = [email.strip() for email in cc_mail.split(',') if email.strip()]
        for i in cc_mails:
            client_socket.sendall(f"RCPT TO: <{i}>\r\n".encode())
            response = client_socket.recv(1024).decode()
            # print(response)
    bcc_mail=input("BCC: ")
    if bcc_mail!='':
        bcc_mails=[]
        bcc_mails = [email.strip() for email in bcc_mail.split(',') if email.strip()]
        for i in bcc_mails:
            client_socket.sendall(f"RCPT TO: <{i}>\r\n".encode())
            response = client_socket.recv(1024).decode()
            #  print(response)
    # Gửi lệnh DATA để bắt đầu viết nội dung email
    client_socket.sendall(b"DATA\r\n")
    response = client_socket.recv(1024).decode()
    # print(response)
    # Messeges 
    if len(recipient_mails) == 1:
        email_string = f'{recipient_mails[0]}'
    else:
        email_string = ', '.join(f'{email}' for email in recipient_mails)
    # print(email_string)
    system_language=locale.getdefaultlocale()[0]
    message= MIMEMultipart()
    message['Message-ID']=make_msgid()
    message.add_header('Content-Language', system_language)
    message['Date']=formatdate(localtime=True)
    message['To']=email_string
    if cc_mail: 
        message['Cc']=cc_mail
    message['From']=mail_from
    message['Subject']=input('Subject: ')
    print("Content (Nhap 2 lan enter de ket thuc phan content): ")
    lines = []
    while True:
        line = input()
        if not line.strip():  # Kiểm tra nếu là dòng trắng
            break
        lines.append(line)
    content = '\n'.join(lines)
    # print(content)
    message.attach(MIMEText(content,"plain"))
    # print(message)
    # Gui file
    flag = input("Có gửi kèm file (1. Yes, 2. No): ")

    if flag == "1":
        count = int(input("Số lượng file muốn gửi: "))
        
        for i in range(1, count + 1):  # Lặp từ 1 đến count (bao gồm count)
            file_path = input(f"file path {i}: ")
            file_size = os.path.getsize(file_path)/(1024**2)
            while file_size>3:
                print("Dung lượng lớn hơn 3mb")
                file_path=input(f"Nhap duong dan file {i}: ")
                file_size = os.path.getsize(file_path)/(1024**2)
            file_name=file_name = os.path.basename(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            with open(file_path, "rb") as attachment:
                part = MIMEBase(*mime_type.split('/'))
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={file_name}",
                )
                message.attach(part)

    text=message.as_string()
    client_socket.sendall(text.encode())
    response=client_socket.recv(1024).decode()



    # Gửi dấu chấm để kết thúc DATA
    client_socket.sendall(b"\r\n.\r\n")
    response = client_socket.recv(1024).decode()
    #print(response)

    # Gửi lệnh QUIT để đóng kết nối
    client_socket.sendall(b"QUIT\r\n")
    response = client_socket.recv(1024).decode()
    #print(response)
    print("\nĐã gửi email thành công\n")
    client_socket.close()
       
# try: 
# SEND_MAIL()
# finally:
#     client_socket.close()

