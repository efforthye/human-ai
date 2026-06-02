# ==========================
# AI 클라이언트 (Requests 기반)
# ==========================
# 사용자 입력을 받아 AI 서버에 분석 요청을 전송하고
# JSON 응답을 받아 콘솔에 출력합니다.
# ==========================

import requests  # HTTP 통신용
import json      # JSON 직렬화/역직렬화용

# -----------------------------------
# 1. 서버 주소 설정
# -----------------------------------
SERVER_URL = "http://192.168.0.127:8000/analyze"

print("AI 서버 클라이언트 시작 (종료하려면 'exit' 입력)\n")

# -----------------------------------
# 2. 사용자 입력 반복
# -----------------------------------
while True:
    # 분석 모드 선택
    mode = input("분석 모드 입력 (length / sentiment / keyword): ").strip()

    # exit 입력 시 종료
    if mode.lower() == "exit":
        print("클라이언트 종료")
        break

    # 분석할 문장 입력
    text = input("분석할 문장 입력: ").strip()

    # -----------------------------------
    # 3. 요청 데이터(JSON) 생성
    # -----------------------------------
    payload = {"mode": mode, "text": text}

    # -----------------------------------
    # 4. POST 요청 전송
    # -----------------------------------
    try:
        response = (requests.post(SERVER_URL, json=payload))
    except requests.exceptions.RequestException as e:
        print(f" 서버 연결 오류: {e}\n")
        continue

    # -----------------------------------
    # 5. 서버 응답 처리
    # -----------------------------------
    if response.status_code == 200:
        # JSON 응답을 보기 좋게 출력
        result = response.json()
        print(f"\n 서버 응답:\n{json.dumps(result, ensure_ascii=False, indent=2)}\n")
    else:
        print(f" 오류 발생: {response.status_code}, {response.text}\n")