# =====================================================
# 멀티 클라이언트 지원 API TCP 클라이언트
# - 사용자가 입력한 요청 (JSON) 을 서버로 전송
# - 서버의 분석 결과를 수신 및 출력
# =====================================================
import socket
import json

# 1. 서버 접속 정보
HOST = "192.168.0.127" # 서버 IP 주소
PORT = 1223 # 사용할 포트 번호 (0~65545 중 하나, 다른 서비스와 중복 금지(고유포트지정))
# HOST = "192.168.0.19" # 서버 IP 주소
# PORT = 9723 # 사용할 포트 번호 (0~65545 중 하나, 다른 서비스와 중복 금지(고유포트지정))
# HOST = "192.168.224.1" # 서버 IP 주소
# PORT = 9222 # 사용할 포트 번호 (0~65545 중 하나, 다른 서비스와 중복 금지(고유포트지정))

# 2. 서버 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print("서버에 연결되었습니다. (종려하려면 'exit'를 입력)\n")

# 3. 송수신 루프
# - 데이터 송수신 할 때는 무조건 while 문으로 처리해야 합니다.
while True:
    # 요청 모드 입력받기
    mode = input("분석 모드 (length / sentiment / keyword) 입력: ").strip()

    if mode.lower() == "exit":
        client_socket.sendall(mode.encode())
        break

    # 분석할 텍스트를 입력
    text = input("분석할 문장 입력: ").strip()

    # 요청 json 구성
    request = {"mode": mode, "text": text}

    # json 직렬화 후 서버로 전송
    client_socket.sendall(json.dumps(request, ensure_ascii=False).encode())

    # 서버로부터 응답 수신
    data = client_socket.recv(2048).decode()

    try:
        response = json.loads(data)
        print(f"\n서버 응답: {json.dumps(response, ensure_ascii=False, indent=2)}\n")
    except json.decoder.JSONDecodeError as e:
        print(f"서버 응답 오류: {data}\n")

# 4. 연결 종료
client_socket.close()
print(f"클라이언트 종료 완료")
