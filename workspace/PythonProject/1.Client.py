# TCP/IP 클라이언트 예제: 사용자가 입력한 메시지를 서버로 전송하고, 서버의 응답을 받아 쿨력하는 클라이언트 기능 실습.

import socket # 네트워크 통신 모듈(socket)

## 1. 서버의 접속 정보 설정
HOST = "192.168.0.127" # 서버 IP 주소
PORT = 1222

## 2. 소켓 생성
## - IPv4(AF_INET) + TCP(SOCK_STREAM) 사용
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

## 3. connect() 서버에 연결 시도
client_socket.connect((HOST, PORT))
print(f"서버 {HOST}:{PORT} 에 연결되었습니다.")
print("메시지를 입력하세요. (종료하려면 'exit' 입력)\n")

## 4. 메시지 송수신 루프
while True:
    # 사용자 입력 대기
    message = input("보낼 메시지: ") # 인풋 함수를 통해 임의의 키보드 텍스트 입력 후 보냄

    # 'exit' 입력 시 종료
    if message.lower() == "exit":
        client_socket.sendall(message.encode()) # 서버에 종료 알림 전송
        break

    # 서버로 메시지 전송
    client_socket.sendall(message.encode())

    # 서버로 응답 수신
    data = client_socket.recv(1024).decode()
    print(f"서버 응답: {data}\n")

# ---------------------------------
# 5. 소켓 종료
# ---------------------------------
client_socket.close()
print("클라이언트 종료 완료")