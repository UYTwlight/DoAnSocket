import socket
import base64
import os
import json 
from email import message_from_string
import re
from email import encoders


# Đọc thông tin file json
file_path="./config.json"
with open(file_path, 'r') as file:
    data = json.load(file)
General_data = data["General"]
filter_data = data["Filter"]

# Thông tin người dùng
EMAIL = data["General"]["Username"]
result = re.search(r'<(.*)>', EMAIL)
if result:
    EMAIL = result.group(1)

# Thông tin server
POP3_SERVER = data["General"]["POP3"]
PORT = data["General"]["MailServer"]
PASSWORD = data["General"]["Password"]

# Thông tin filter
from_filter = filter_data["From"]
subject_filter = filter_data["Subject"]
content_filter = filter_data["Content"]
spam_filter = filter_data["Spam"]
filter_folder = ["Inbox",from_filter["Folder"], subject_filter["Folder"], content_filter["Folder"], spam_filter["Folder"]]


# Kết nối pop3 server
def connect():
    # Tạo kết nối socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # print(client_socket)
    client_socket.connect((PORT, POP3_SERVER))
    # Nhận và in phản hồi từ máy chủ
    response = client_socket.recv(1024).decode()
    # print(response)
    # Gửi USER và nhận phản hồi
    client_socket.sendall(f'USER {EMAIL}\r\n'.encode('utf-8'))
    response = client_socket.recv(1024).decode()
    # print(response)
    # Gửi PASS và nhận phản hồi
    client_socket.sendall(f'PASS {PASSWORD}\r\n'.encode('utf-8'))
    response = client_socket.recv(1024).decode()
    # print(response)
    # Gửi STAT để lấy thông tin về số lượng email và kích thước của chúng
    client_socket.sendall(b'STAT\r\n')
    response = client_socket.recv(1024).decode()
    # print(response)
    # Gửi LIST để lấy danh sách email 
    client_socket.sendall(b'LIST\r\n')
    response = client_socket.recv(1024).decode()
    # print(response)
    # Gửi UIDL để lấy danh sách email với UID (Unique Identifier)
    client_socket.sendall(b'UIDL\r\n')
    response = client_socket.recv(1024).decode()
    # print(response)
    #tách chuỗi
    parts = response.split('\r\n')
    #bỏ dòng đầu và 2 dòng cuối
    parts=parts[1:]
    parts=parts[:-2]
    # mail_list = parts
    number_of_mail=len(parts)

    
    msg = []    # Mảng email được lấy từ mailbox
    for mail in parts:
        msg.append(mail[2:])
    
    result = [client_socket,number_of_mail,msg]
    return result


# Khởi tạo các filter
def create_folder(file_path):
    for fil in filter_folder:
        if not os.path.exists(file_path + "/" + fil):
            os.makedirs(file_path + "/" + fil)


# Xử lí dữ liệu và tải file về từ mailbox
def decode_base64_to_file(base64_data, output_directory, filename):
    # Giải mã chuỗi base64 thành dữ liệu nhị phân
    binary_data_decoded = base64.b64decode(base64_data)
    # Lấy phần mở rộng và tên file riêng lẻ
    file_name, file_extension = os.path.splitext(filename)
    # Ghi dữ liệu nhị phân vào tệp tin mới với định dạng tương ứng
    output_path = os.path.join(output_directory, f"{file_name}{file_extension}")
    # print(output_path)
    with open(output_path, "wb") as output_file:
        output_file.write(binary_data_decoded)
    print("Đã lưu thành công")
    return output_path




def extract_file(filename, base64_data): 
    # Tên của tệp tin đầu vào
    # Đường dẫn đến thư mục đầu ra
    print("Nhập địa chỉ bạn muốn lưu file:",filename,"(nhấn <enter> để hủy)")
    choice = '1'
    while choice=='1':
        output_directory = input()
        if output_directory=='0': 
            break
        elif os.path.exists(output_directory):
            decode_base64_to_file(base64_data, output_directory, filename)
            break
        else:  
            print("Đường dẫn không tồn tại")
            choice = input("Bạn có muốn nhập lại đường dẫn không?(1. Có; 2. Không): ")


# Xử lí thông tin mail loại 2 (kèm file)
def get_content(parts,msg):
    header_data=parts[0].split("\r\n\r\n", 1)[0].strip()    #da co duoc header data
    # print(header_data)
    from_index = header_data.find('From:')
    subject_index = header_data.find('Subject:')
    date_index=header_data.find('Date:')
    to_index=header_data.find('To:')
    # Trích xuất thông tin người gửi và tiêu đề của email dựa trên vị trí từ khóa
    if from_index != -1 and subject_index != -1:
        from_line = header_data[from_index:subject_index]
        subject_line = header_data[subject_index:]
        date_line=header_data[date_index:]
        to_line=header_data[to_index:]
        name_line=from_line[:-1]
        # Trích xuất thông tin người gửi và tiêu đề từ các dòng vừa trích xuất
        sender = from_line.split('From: ')[-1].split('<')[-1].split('>')[0]
        subject = subject_line.split('Subject: ')[-1].split('\n')[0]
        date = date_line.split('Date: ')[-1].split('\n')[0]
        to = to_line.split('To: ')[-1].split('\n')[0]

    # print(name_line)
    
    # print(match)

    match = re.search(r'=\?UTF-8\?B\?([A-Za-z0-9+/=]+)\?=', name_line)
    if match:
        # print("xin caho")
        encoded_text = match.group(1)
        # print(encoded_text)
        decoded_text = base64.b64decode(encoded_text).decode('utf-8')  #giải mã tên name base64
        # print(decoded_text)
        name = decoded_text.split('=?')[0].strip()
        # print(name)
        name_sender=name+" <"+sender+">"
        # print(name_sender)
    else:
        name_sender= from_line.split('From: ')[-1]
        # print(name_sender)
    # print(name_sender)
    info = [date,name_sender,to,subject]




    # info = [date,sender,to,subject]
    info = "\n".join(info)

    # print(info)
    # print(date) #ngày tháng
    # print(sender) #người gửi
    # print(subject) #subject
    # print(to)   # đến 
    text_plain_part = parts[1]  
    octet_stream_parts = parts[2:]
    # print(octet_stream_parts)
    raw_content = text_plain_part.split("\r\n\r\n", 1)[1].strip() #da co duoc content  
    # print(text_plain_data)
    # Decode base64
     #file raw cần lưu (khi mà người dùng muốn lưu file thì chạy hàm extract
    list_of_os_filename=[] #chứa thông tin thô có tên file 
    list_of_base64=[] #chứa nhũng base64 (ch biết có nào đọc k được hay không)
    for os_part in octet_stream_parts:
        os_part=os_part.strip()
        # print(os_part)
       
        os_data_name = os_part.split("\r\n\r\n", 1)[0].strip() #tách phần os_part ra os_data_name //lấy đc 3 dòng đầu
       
        # print(os_data_name)
        os_data_file = os_part.split("\r\n\r\n", 0)[0].strip() #tách phần os_part ra os_data_file //lấy được full
        os_data_file = os_data_file.split("\r\n") #tách ra để bỏ dòng
        os_data_file = os_data_file[4:] #bỏ 3 dòng và 1 dấu cách
        os_data_file="\r\n".join(os_data_file) #nối lại tạo thành chuỗi base64
        # print(os_data_file)
        list_of_os_filename.append(os_data_name.split('\r\n'))  #cho từng filename chưa xử lí vào list
        # print(list_of_os_filename)
        list_of_base64.append(os_data_file)      #cho từng base64 chưa xử lí vào list
    list_of_os_filename=list_of_os_filename[:-1] #loai bo dấu '.' cuối
    # print(list_of_os_filename)
    list_of_filename=[] #tao mang chua ten cac file co trong mail
    list_of_base64filename=[] #tạo base64 ứng với index tên mail
    # print(list_of_filename)
    for filename in list_of_os_filename:
        # print(filename)
        i=list_of_os_filename.index(filename)
        # print(i)
        list_of_os_filename[i]='\n'.join(list_of_os_filename[i])  #nối lại os_filename thứ i
        # print(list_of_os_filename)
        filename_match = re.search(r'filename="(.+)"', list_of_os_filename[i]) #tìm tên
        if filename_match == None:
            filename_match = re.search(r'filename=(.+)', list_of_os_filename[i]) #tìm tên
        # print(filename_match)
        if filename_match:
            filename = filename_match.group(1)
        else:
            print("Error to download file!")       #nếu không có thì ko thêm vô gì cả, chạy tiếp
            continue
        list_of_filename.append(filename)   #nếu có thì thêm bô list filename, 
        list_of_base64filename.append(list_of_base64[i])    #thêm nội dung mail base64 ứng với index file được lấy
    # print(list_of_filename)

    i=0
    s_base64 =[]
    for i in range(0,len(list_of_filename)):
        # print(s_base64)
        s_base64.append(list_of_filename[i])
        s_base64.append(list_of_base64filename[i])
    
    
    s_base64 ="\n\n".join(s_base64)
    file_path = "./debug/" + EMAIL
    create_folder(file_path)

    # Lọc email
    if create_msg(spam_filter["Keyword"],spam_filter["Folder"],sender,info,raw_content,msg,s_base64)!=True:
        if create_msg(subject_filter["Keyword"],subject_filter["Folder"],sender,info,raw_content,msg,s_base64)!=True:
            if create_msg(from_filter["Keyword"],from_filter["Folder"],sender,info,raw_content,msg,s_base64)!=True:
                if create_msg(content_filter["Keyword"],content_filter["Folder"],sender,info,raw_content,msg,s_base64)!=True:
                    if not os.path.exists(file_path + "/" + filter_folder[0]+"/"+ msg):
                        os.makedirs(file_path + "/" + filter_folder[0]+"/"+ msg)
                    with open("./debug/"+EMAIL+"/"+filter_folder[0]+"/"+ msg+"/info", 'wb') as file_result:
                        file_result.write(info.encode())
                    with open("./debug/"+EMAIL+"/"+filter_folder[0]+"/"+ msg+"/content", 'wb') as file_result:
                        file_result.write(raw_content.encode())
                    with open("./debug/"+EMAIL+"/"+filter_folder[0]+"/"+ msg+"/base64", 'wb') as file_result:
                        file_result.write(s_base64.encode())




# Kiểm tra file "msg" có trong đường đẫn không
def check_file(file_path,folder,msg):
    file = os.listdir(file_path+"/"+folder)
    for i in file:
        if i == msg:
            return True
    return False

def check_base64(file_path):
    file = os.listdir(file_path)
    for i in file:
        if i == "base64":
            return True
    return False


# Khởi tạo file msg chứa chủ đề + nội dung
def create_msg(key,filter_folder,sender,subject,content,msg,base64=None):
    for i in range(len(key)):
        if filter_folder=="Project":
            flag = sender.find(key[i])
        if filter_folder=="Important":
            flag = subject.find(key[i])
        if filter_folder=="Work":
            flag = content.find(key[i])
        if filter_folder=="Spam":
            flag = subject.find(key[i])
            if flag == -1:
                flag = content.find(key[i])
        if flag != -1:
            # shutil.move(file_path +"/"+ msg, file_path +"/"+ from_filter["Folder"])
            file_path = "./debug/"+EMAIL
            if not os.path.exists(file_path + "/" + filter_folder+"/"+ msg):
                os.makedirs(file_path + "/" + filter_folder+"/"+ msg)
            with open("./debug/"+EMAIL+"/"+filter_folder+"/"+ msg+"/info", 'wb') as file_result:
                file_result.write(subject.encode())
            with open("./debug/"+EMAIL+"/"+filter_folder+"/"+ msg+"/content", 'wb') as file_result:
                file_result.write(content.encode())
            if base64!=None:
                with open("./debug/"+EMAIL+"/"+filter_folder+"/"+ msg+"/base64", 'wb') as file_result:
                    file_result.write(base64.encode())
            return True
            # break
    return False
    


# def locmail(key,sender,subject,content,msg,base64=None):
#     for i in range(len(key)):
#         if filter_folder=="Spam":
#             flag = subject.find(key[i])
#             if flag == -1:
#                 flag = content.find(key[i])
#             if flag !=-1:
#                 create_msg()
#         elif filter_folder=="Important":
#             flag = subject.find(key[i])
#             if flag !=-1:
#                 create_msg()
#         elif filter_folder=="Work":
#             flag = content.find(key[i])
#             if flag !=-1:
#                 create_msg()
#         elif filter_folder=="Project":
#             flag = sender.find(key[i])
#             if flag !=-1:
#                 create_msg()
#         else:

#     # return True
#     # Lọc email
#     create_msg(from_filter["Keyword"],from_filter["Folder"],sender,info,raw_content,msg,base64)
#     create_msg(subject_filter["Keyword"],subject_filter["Folder"],sender,info,raw_content,msg,base64)
#     create_msg(content_filter["Keyword"],content_filter["Folder"],sender,info,raw_content,msg,base64)
#     create_msg(spam_filter["Keyword"],spam_filter["Folder"],sender,info,raw_content,msg,base64)
#     flag = 0
#     for i in range(len(filter_folder)-1):
#         if not os.path.exists(file_path + "/" + filter_folder[i+1]+"/"+ msg):
#             flag+=1
#     if flag == 4:
#         if not os.path.exists(file_path + "/" + filter_folder[0]+"/"+ msg):
#             os.makedirs(file_path + "/" + filter_folder[0]+"/"+ msg)
#         with open("./debug/"+EMAIL+"/"+filter_folder[0]+"/"+ msg+"/info", 'wb') as file_result:
#             file_result.write(subject.encode())
#         with open("./debug/"+EMAIL+"/"+filter_folder[0]+"/"+ msg+"/content", 'wb') as file_result:
#             file_result.write(content.encode())
#         with open("./debug/"+EMAIL+"/"+filter_folder[0]+"/"+ msg+"/base64", 'wb') as file_result:
#             file_result.write(base64.encode())

# Đọc email và lọc email
def decode_type1(mail_content, msg):
    # print("Content: ")
    # print(mail_content)
    

    # print("Content: ")
    # print(mail_content)
    header_data=mail_content
    # print(header_data)
    # print(header_data)
    from_index = header_data.find('From:')
    subject_index = header_data.find('Subject:')
    date_index=header_data.find('Date:')
    to_index=header_data.find('To:')
    # Trích xuất thông tin người gửi và tiêu đề của email dựa trên vị trí từ khóa
    if from_index != -1 and subject_index != -1:
        # print(subject_index)
        name_line=header_data[from_index:subject_index]
        from_line = header_data[from_index:subject_index-1]

        # print(from_line)
        subject_line = header_data[subject_index:]
        date_line=header_data[date_index:]
        to_line=header_data[to_index:]
        # Trích xuất thông tin người gửi và tiêu đề từ các dòng vừa trích xuất
       
        
        match = re.search(r'=\?UTF-8\?B\?([A-Za-z0-9+/=]+)\?=', name_line)
        # print(match)
        # name = decoded_text.split('=?')[0].strip()
        sender =from_line.split('From: ')[-1].split('<')[-1].split('>')[0]
        subject =subject_line.split('Subject: ')[-1].split('\r\n')[0]
        date =date_line.split('Date: ')[-1].split('\r\n')[0]
        to = to_line.split('To: ')[-1].split('\r\n')[0] 
    # print(name)
        name_sender=""
        if match:
            # print("xin caho")
            encoded_text = match.group(1)
            decoded_text = base64.b64decode(encoded_text).decode('utf-8')  #giải mã tên name base64
            name = decoded_text.split('=?')[0].strip()
            # print(name)
            name_sender=name+" <"+sender+">"
            # print(name_sender)
        else:
            name_sender= from_line.split('From: ')[-1]
            # print(name_sender)
    
    # name_sender=name+" <"+sender+">"
    # print(name_sender)
    info = [date,name_sender,to,subject]
    info = "\n".join(info)
    # print(info)
    
    start_index = mail_content.find('Content-Type: text/plain')
    if start_index != -1:
    # Lấy phần nội dung sau dòng "Content-Type: text/plain"
        content = mail_content[start_index:]
        # Xóa các thông tin không cần thiết ở phần nội dung
        content = content.split('\n\n', 1)[-1]
        #tách ra để chuẩn bị xóa 3 dòng đầu 3 dòng cuối
        content=content.split("\r\n")
        content=content[3:-3]
        content="\r\n".join(content)
        # print(content) #đã có được content
        raw_content=content
    # Tạo các filter trong email
    file_path = "./debug/" + EMAIL
    create_folder(file_path)

    # Lọc email
    if create_msg(spam_filter["Keyword"],spam_filter["Folder"],sender,info,raw_content,msg)!=True:
        if create_msg(subject_filter["Keyword"],subject_filter["Folder"],sender,info,raw_content,msg)!=True:
            if create_msg(from_filter["Keyword"],from_filter["Folder"],sender,info,raw_content,msg)!=True:
                if create_msg(content_filter["Keyword"],content_filter["Folder"],sender,info,raw_content,msg)!=True:
                    if not os.path.exists(file_path + "/" + filter_folder[0]+"/"+ msg):
                        os.makedirs(file_path + "/" + filter_folder[0]+"/"+ msg)
                    with open("./debug/"+EMAIL+"/"+filter_folder[0]+"/"+ msg+"/info", 'wb') as file_result:
                        file_result.write(info.encode())
                    with open("./debug/"+EMAIL+"/"+filter_folder[0]+"/"+ msg+"/content", 'wb') as file_result:
                        file_result.write(raw_content.encode())
        
    
    # flag = 0
    # for i in range(len(filter_folder)-1):
    #     if not os.path.exists(file_path + "/" + filter_folder[i+1]+"/"+ msg):
    #         flag+=1
    # if flag == 4:
        


def decode_type2(mail_content, msg):
    # print("TYPE 2\n")
    # Chuyển đổi chuỗi email thành đối tượng Message
    mail_message = message_from_string(mail_content)
    # print(mail_message)
    # Lấy boundary từ email_message
    boundary = mail_message.get_boundary()
    # print(boundary)
    # Tách các phần MIME dựa trên boundary
    parts = mail_content.split(f'--{boundary}')
    # print(parts)
     # In ra từng phần MIME đã tách
    # for part in parts:
    #     print(part.strip())
    #     print('-' * 30)
    get_content(parts,msg)


def decode (mail_content, msg):
     # In ra phần header và phần nội dung đã tách)
    parts = mail_content.split('\n')
    sub_string1="Message-ID"
    sub_string2="Content-Type"
    if sub_string1 in parts[0]: decode_type1(mail_content, msg)
    if sub_string2 in parts[0]: decode_type2(mail_content, msg)


def get_response(client_socket):
    response =b""
    while True:
        mail_content = client_socket.recv(1024)
        response+=mail_content
        if len(mail_content)<1024:
            break

# Load thông tin email về từ mailbox
def load(client_socket,number_of_mail,msg):
    for i in range(number_of_mail):
        client_socket.sendall(f"RETR {i+1}\r\n".encode())
        response =b""
        while True:
            mail_content = client_socket.recv(1024)
            response+=mail_content
            if len(mail_content)<1024:
                break
        mail_content = response.decode('utf-8')
        parts = mail_content.split('\n')
        parts=parts[1:]
        mail_content='\n'.join(parts)
        decode(mail_content, msg[i])

# Đóng  kết nối pop3 server
def quit_pop3_server(client_socket):
    # Gửi lệnh QUIT và đóng kết nối
    client_socket.sendall(b"QUIT\r\n")
    client_socket.close()

# Chạy Reload server
def active():
    result = connect()
    load(result[0],result[1],result[2])
    quit_pop3_server(result[0])




# Xem nội dung email
def view(file_path):
    # Đọc chủ đề + nội dung từ file
    f_subject = open(file_path+"/info", "r", encoding = "utf-8")
    f_content = open(file_path+"/content","r", encoding = "utf-8")
    mail_subject = f_subject.read()
    mail_content = f_content.read()
    # In ra chủ đề + nội dung email
    mail_subject=mail_subject.split('\n')
    mail_subject[0]="Date: " +mail_subject[0]
    mail_subject[1]="From: " +mail_subject[1]
    mail_subject[2]="To: " +mail_subject[2]
    mail_subject[3]="Subject: " +mail_subject[3]
    mail_subject = "\n".join(mail_subject)
    print(mail_subject,"\n")
    mail_content = "Content: " +mail_content
    print(mail_content,"\n")
    # Khởi tạo file "seen" khi đã đọc email
    with open(file_path + "/seen", 'wb') as file_result:
        file_result.write("seen".encode())
        
        
    if check_base64(file_path) == True:
        # print(file_path)
        f_base64 = open(file_path+"/base64", "rt")
        base64=f_base64.read()
        base64=base64.split("\n\n")
        print("Mail này có chứa file: ")
        i=0
        while i*2<len(base64):
            print(i+1, base64[i*2])
            i+=1
        choice = input("Bạn có muốn lưu file không (1. Có; 2. Không): ")
        if choice == '1':
            i=0
            while i<len(base64):
                extract_file(base64[i],base64[i+1])
                i+=2
        f_base64.close()
        

    f_subject.close()
    f_content.close()
    


# Xem danh sách email trong folder
def view_list_mail(file_path):

    # Tạo các filter cho email không có trên mailbox
    last_slash_index = file_path.rfind('/')
    create = file_path[:last_slash_index]
    create_folder(create)

    # Đường dẫn không có file thì trả về
    file_names = os.listdir(file_path)
    if file_names==[]:
        return False
    
    # In ra tên các file trong thư mục
    # Tạo mảng chứa tên các file email
    mail_list = []
    for file_name in file_names:
        mail_list.append(file_name)
    
    # Xuất trạng thái từng file email
    for i in range(1, len(mail_list)+1):
        seen = "(chưa đọc) "
        file_check = os.listdir(file_path+"/"+file_names[i-1])
        for file in file_check:
            if file == "info":
                f = open(file_path+"/"+mail_list[i-1]+"/info", "r",encoding="utf-8")
                data = f.read()
                
                data = data.split('\n')
                sender = data[1]
                # print(sender)

                subject='<'+data[3]+'>'
                data='\n'.join(data)

                f.close()
            if file == "seen":
                seen = ""
                
        print(f"{i}. {seen}{sender} {subject}")



active()