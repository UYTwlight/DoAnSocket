from pop3 import view_list_mail,view, active, General_data, filter_folder, EMAIL
from smtp import SEND_MAIL
import socket
import time
import threading
import os



# Thông tin người dùng
username = General_data["Username"]
psw = General_data["Password"]
smtp_port = General_data["SMTP"]
pop3_port = General_data["POP3"]
server = General_data["MailServer"]
autoload = General_data["Autoload"]


# In ra người dùng
print("Tên người dùng:", username)


# Hàm xem email đã chọn trong folder
def view_email(folder_path):
    if view_list_mail(folder_path) == False:
        print("Khong co email nao trong folder")
        return
    choice = input("Chon email ban muon xem: ")
    if choice == '' or choice =='0':
        return
    folder_choose = os.listdir(folder_path)
    view(folder_path + "/" + folder_choose[int(choice)-1])


# Load Test_mail_server mỗi Autoload
def load():
    while True:
        active()
        time.sleep(autoload)


# Menu
while True:
    pop_thread = threading.Thread(target=load)
    pop_thread.daemon = True
    pop_thread.start()
    print("Vui lòng chọn menu:")
    print("1. Để gửi email")
    print("2. Để xem danh sách các email đã nhận")
    print("3. Thoát")
    option = input("Bạn chọn: ")
    if option == '1':
        print("Đây là thông tin soạn email: (nếu không điền vui phòng nhấn <enter> để bỏ qua)")
        SEND_MAIL(None)
    elif option == '2':
        while True:
            print("Đây là danh sách các folder trong mailbox của bạn:")
            for i in range(len(filter_folder)):
                print(f"{i+1}. {filter_folder[i]}")
            option_2 = input("Bạn muốn xem email trong folder nào: ")
            folder_path = "./debug/" + EMAIL
            if option_2 == '' or option_2 == '0':
                break
            elif option_2.isdigit() and 1 <= int(option_2) <= 5:
                if option_2 == '0' or option_2 == '':
                    break
                elif option_2 == '1':
                    print("Đây là danh sách email trong Inbox folder:")
                    folder_path += "/Inbox"
                    view_email(folder_path)
                elif option_2 == '2':
                    print("Đây là danh sách email trong Project folder:")
                    folder_path += "/Project"
                    view_email(folder_path)
                elif option_2 == '3':
                    print("Đây là danh sách email trong Important folder:")
                    folder_path += "/Important"
                    view_email(folder_path)
                elif option_2 == '4':
                    print("Đây là danh sách email trong Work folder:")
                    folder_path += "/Work"
                    view_email(folder_path)
                elif option_2 == '5':
                    print("Đây là danh sách email trong Spam folder:")
                    folder_path += "/Spam"
                    view_email(folder_path)
            else:
                print("Nhập sai. Hãy nhập lại lựa chọn.")
    elif option == '3':
        print("Exiting...")
        break
    else:
        print("Nhập sai. Hãy nhập lại lựa chọn.")