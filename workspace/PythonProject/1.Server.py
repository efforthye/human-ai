import socket # 네트워크 통신을 위한 기본 모듈

## 1. 서버 기본 설정 (로컬서버 아이피 주소 확인)
HOST = "192.168.0.127" # 서버 IP 주소
PORT = 1222 # 사용할 포트 번호 (0~65545 중 하나, 다른 서비스와 중복 금지(고유포트지정))

## 2. socket() 소켓 객체 생성
# socket.AF_INET: IPv4 주소체계 사용
# socket.SOCK_STREAM: TCP 프로토콜 사용
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

## 3. bind() IP와 포트를 소켓에 바인딩(연결)
# - 서버가 클라이언트 요청을 받을 수 있도록 설정
server_socket.bind((HOST, PORT))

## 4. listen() 클라이언트 연결 대기 시작(서버 구동시 리스닝 함수)
# - 인자 없이 listen() 호출 시, 기본적으로 동시 접속 1개만 허용
server_socket.listen()

print(f"서버가 {HOST}:{PORT} 에서 연결 대기 중입니다...")

## 5. accept() 클라이언트 연결 수락: 클라이언트가 접속할 때까지 블로킹 상태로 대기 -> 연결이 발생하면(클라이언트 소켓, 클라이언트 주소) 튜플 반환
client_socket, addr = server_socket.accept()
print(f"클라이언트 {addr} 연결 완료")

## 6. recv()/send() 클라이언트와 메시지 송수신 루프
while True:
    # 클라이언트로부터 최대 1024바이트 데이터 수신 가능
    data = client_socket.recv(1024).decode() # 클라이언트로부터의 메시지 bytes를 str(문자열)로 변환
    if not data:
        # 클라이언트 연결이 끊기면 루프 종료
        print("데이터 수신 종료(클라이언트 연결 해제됨)")
        break
    # 종료 명령 감지
    if data.lower() == "exit": # 수동 해제
        print("데이터 수신 종료(클라이언트 연결 해제됨)")
        break

    # 수신된 메시지 출력
    print(f"클라이언트 메시지: {data}")

    # 서버의 응답 생성
    reply = f"서버 응답: [{data}] 잘 받았습니다."

    # 클라이언트로 응답 전송 (문자열 그냥 보내는 게 아니라, bytes로 변환해서 보냄)
    client_socket.sendall(reply.encode())

## 7. 연결 종료
client_socket.close()
server_socket.close()
print("서버 종료 완료")