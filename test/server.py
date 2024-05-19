from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import queue
import mysql.connector


#받고 보내고
class StreamTCPsocket():
    def __init__(self,socket:socket,address):
        self.__socket=socket 
        self.__address=address

    def recv(self):
        data=self.__socket.recv(1024).decode()
        return data
    
    def send(self, send_data):
        self.__socket.send(send_data.encode())
        


#string -> dict , dict ->string
class RealtimeServiceProtocol:
    def __init__(self):
        return
    
    # string data를 dict로 바꾸는 친구 
    def str_to_dict(self,data:str):
        list_data=data.split(" ") 
        dict_data = self.__method_checker(list_data[0])
        i = 1
        for k in dict_data.keys():
            dict_data[k] = list_data[i]
            i += 1

        return dict_data 
    
    def __method_checker(self, method):
        
        dict_data = {}
        #로그인
        if method == "Login":
            dict_data = {"method":"Login",
                         "ID" :"assd",
                         "PW" :"dsagdsag",
            }

        #gps 데이터 전송
        elif method == "Gps":
            dict_data = {"method":"Gps",
                         "X" :"13.00",
                         "Y" :"14.00",
            }

        #회원가입
        elif method == "SignUp":
            dict_data ={"method":"SignUp",
                        "name":"김나은",
                        "guardNumber": "01030236298",
                        "patientNumber":"01011235677",
                        "address":"대구광역시",
                        "id":"adfadf",
                        "pw":"dafdsfa",

            }

        return dict_data

    # string data를 dict로 바꾸는 친구 
    def dict_to_str(self, data:dict):
        str_data = ""
        for value in data.values():
            str_data += value + " "

        return str_data    


#클라이언트 모델
class ClientModel:
    def __init__(self):
        self.__id = ""
        self.__pw = ""
        self.__address = ""
        self.__name = ""
        self.__patientNumber = ""
        self.__guardianNumber = ""
    
    def set_id(self, id):
        self.__id = id
    
    def set_pw(self, pw):
        self.__pw = pw
    
    def set_address(self, address):
        self.__address = address
    
    def set_name(self, name):
        self.__name = name

    def set_patientNumber(self, patientNumber):
        self.__patientNumber = patientNumber

    def set_guardianNumber(self, guardianNumber):
        self.__guardianNumber = guardianNumber

    def get_id(self):
        return self.__id

    def get_pw(self):
        return self.__pw

    def get_name(self):
        return self.__name

    def get_address(self):
        return self.__address

    def get_patientNumber(self):
        return self.__patientNumber

    def get_guardianNumber(self):
        return self.__guardianNumber

# DB_API 클래스
class DB_API:
    def __init__(self):
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1017",
            database='patient'
        )
        self.cursor = self.mydb.cursor()

    def insert_client(self, client):
        query = "INSERT INTO patient (id, pw, address, name, patient_number, guardian_number) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (
            client.get_id(),
            client.get_pw(),
            client.get_address(),
            client.get_name(),
            client.get_patientNumber(),
            client.get_guardianNumber()
        )
        self.cursor.execute(query, values)
        self.mydb.commit()
        print("회원가입이 완료되었습니다.")

    def check_id_exist(self, id):
        query = "SELECT id FROM patient WHERE id = %s"
        self.cursor.execute(query, (id,))
        result = self.cursor.fetchone() 

        if result:
            return True  
        else:
            return False  

    def __verify_password(self, id, pw):
        query = "SELECT pw FROM patient WHERE id = %s"
        self.cursor.execute(query, (id,))
        result = self.cursor.fetchone()

        if result and result[0] == pw:
            return True
        else:
            return False

    def close_connection(self):
        self.cursor.close()
        self.mydb.close()

# LoginController 클래스
class LoginController:
    def __init__(self, DB):
        self.__DB = DB
    
    def try_login(self, id, pw):
        if self.__DB.check_id_exist(id):
            print("아이디 존재")
            if self.__DB.verify_password(id, pw):
                print("로그인 성공")
            else:
                print("비밀번호가 올바르지 않습니다")
        else:
            print("아이디 존재하지 않음")
    
    def sign_up(self, id, pw, name, address, patientNumber, guardianNumber):
        newClient = ClientModel()
        newClient.set_id(id)
        newClient.set_pw(pw)
        newClient.set_name(name)
        newClient.set_address(address)
        newClient.set_patientNumber(patientNumber)
        newClient.set_guardianNumber(guardianNumber)
        newClient.set_pid(id)
        self.__DB.insert_client(newClient)

#채팅방 - 환자와 보호자 짝찾아주는 클래스? 하나의 방 느낌        
class ChattingRoom():

    def __init__(self, pid):
        self.__pid = pid
        self.__recv_que_p = queue.Queue()
        self.__send_que_p = queue.Queue()
        self.__recv_que_g = queue.Queue()
        self.__recv_que_g = queue.Queue()
        self.__client = []

    def input_client(self, client):
        self.__client.append(client)
        return 

    def set_pid(self, pid):
        self.__pid = pid

    def get_pid(self):
        return self.__pid

    ############환자###############        
   #큐에 비어있는지? 
    def patient_is_queue_empty(self):
        result = self.__send_que_p.empty()
        return result

    #recv큐에서 값 빼기
    def patient_recv_dequeue(self,):
        data = self.__recv_que_p.get()
        return data
   
    #recv큐에 값 넣기
    def patient_recv_enqueue(self, data):
        self.__recv_que_p.put(data)
        return

    #send큐에 값 빼기 
    def patient_send_dequeue(self,):
        data = self.__send_que_p.get()
        return data
   
    #send큐에 값 넣기 
    def patient_send_enqueue(self, data):
        self.__send_que_p.put(data)
        return
    
    #############보호자쪽###############

    #보호자 큐 비어있는지 확인 
    def guardian_is_queue_empty(self):
        result = self.__send_que_g.empty()
        return result

    #recv 큐에서 값 빼기
    def guardian_recv_dequeue(self,):
        data = self.__recv_que_g.get()
        return data
   
    #recv 큐에서 값 넣기
    def guardian_recv_enqueue(self, data):
        self.__recv_que_g.put(data)
        return

    #send 큐에서 값 빼기
    def guardian_send_dequeue(self,):
        data = self.__send_que_g.get()
        return data
   
    #send큐에서 값 넣기
    def guardian_send_enqueue(self, data):
        self.__send_que_p.put(data)
        return

# 채팅룸을 관리하고 인터페이스를 제공하는 클래스
class ChattingRoomAPI:
    def __init__(self):
        self.chattingrooms = []  # 채팅룸 리스트

    #채팅룸 찾기
    def find_room(self, room_name):
        for room in self.chattingrooms:
            if room == room_name:
                return room
        return False

    
    #채팅룸이 없으면 생성하기 
    def create_room(self, room_name):
        chattingRoom =ChattingRoom(room_name)
        chattingRoom.set_pid(room_name)

        self.chattingrooms.append(newroom)
        return chattingRoom

    #채팅룸 반환
    def get_room(self, room_name):
        return self.find_room(room_name)

    #클라이언트 추가하기
    def add_client_room(self, room_name, client):
        chattingRoom = self.find_room(room_name)
        if not chattingRoom:
            chattingRoom = self.create_room(room_name)
        chattingRoom.input_client(client)
        return chattingRoom


    
import time
#비동기서버 만드는 인터페이스
class RealTimeServiceASGI:
    def __init__(self):
        pass

    def run_server(self):
        print("[ start server")
        self.__start_server()
        

    def __start_server(self):
        ip = "127.0.0.1"
        port = 9999
        server_socket = socket(AF_INET, SOCK_STREAM)
        server_socket.bind(('127.0.0.1',9999))
        print(f"ip : {port}  | port = {str(port)}")
        server_socket.listen()
        realtimeServiceProtocol = RealtimeServiceProtocol()
        while True:
            client_socket, client_addr = server_socket.accept()
            streamTCPSocket = StreamTCPsocket(socket=client_socket,
                                                address=client_addr)
            func = self.__client_Handle_Thread
            client_Handle_Thread = Thread(target=func, 
                                     args=(streamTCPSocket,realtimeServiceProtocol))
            client_Handle_Thread.start()

    #소켓끼리 데이터 송수신
    def recv_thread(self,streamTCPsocket,realTimeServiceProtocol,chattingRoom):
        while True:
            if not chattingRoom.is_queue_empty():
                data = StreamTCPsocket.recv()
                dict_data = RealtimeServiceProtocol.str_to_dict(data)
                ChattingRoom.enqueqe(dict_data)
            else:
                print("큐에 데이터를 넣을 준비가 되지 않았습니다.")


    def send_thread(self,streamTCPsocket,realTimeServiceProtocol,chattingRoom):
        while True:
            if not chattingRoom.is_queue_empty():
                data = chattingRoom.dequeue()
                if data == True:
                    chattingRoom.dequeqe(data)
                str_data = RealtimeServiceProtocol.dict_to_str(data)
                StreamTCPsocket.send(str_data)
            else:
                print("큐에 전송할 데이터가 없습니다.")
   

    def __client_Handle_Thread(self, streamTCPSocket:StreamTCPsocket, realTimeServiceProtocol):
        #send_data = "hello" 
        #send_data = send_data.encode()
        #streamTCPSocket.send(send_data)        
        #print("send clear")
        #print(recv_data)
        #time.sleep(5)

        recv_data = streamTCPSocket.recv()
        recv_dict_data = realTimeServiceProtocol.str_to_dict(recv_data)
        chatting_room_api = ChattingRoomAPI()

        room_name = recv_dict_data['id']
        client = recv_dict_data['who']
        
        if chatting_room_api.find_room(room_name):
            chatiing_room_api.add_client_room(room_name)
        else:
            chatting_room_api.create_room(room_name)
            chatting_room_api.add_client_room(room_name,who)
    
        recv_thread = Thread(target=self.recv_thread, 
                         args=(streamTCPSocket, realTimeServiceProtocol, room_name))
        send_thread = Thread(target=self.send_thread, 
                         args=(streamTCPSocket, realTimeServiceProtocol, room_name))


        recv_thread.start()
        send_thread.start()
        recv_thread.join()
        send_thread.join()

        print("End of procedure")
        
        # 1. recv 한번 받기
        # 2. recv 받은 데이터 RSTP에서 데이터 변환
        # 3. 변환한 데이터 가지고 체팅방 찾기
        # 4. 채팅방 찾으면 들어가기
        # 5. 없으면 만들기
        # 6. recvTHread만들고
        # 7. sendThread 만들고
        # 8. 생성한 각강의 스레드 start()
        # 9. 대기 하다가 join()
        # 10. end of procedure

if __name__ == "__main__":
    realTimeServiceASGI = RealTimeServiceASGI()
    realTimeServiceASGI.run_server()

    logincontroller = LoginController()
    data = {''} # 가짜 데이터
    result = logincontroller.try_login(data)
    print(result)