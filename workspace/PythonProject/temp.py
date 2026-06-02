import requests

url = "http://192.168.0.19:8000/analyze"

print("\n===== 분석 모드 =====")
print("1. length")
print("2. sentiment")
print("3. keyword")
print("4. Chat")
print("exit : 종료")

mode = input("분석 모드 입력: ")

# 채팅 모드
if mode in ["4", "chat"]:
    print("채팅 모드 시작 (종료: exit)")

    while True:
        text = input("나: ")

        if text.lower() == "exit":
            print("채팅 종료")
            break

        data = {
            "mode": mode,
            "text": text
        }

        response = requests.post(url, json=data)
        result = response.json()

        print("봇:", result["result"])

# 일반 분석
else:
    while True:
        text = input("문장 입력 (종료: exit): ")

        if text.lower() == "exit":
            print("프로그램 종료")
            break

        data = {
            "mode": mode,
            "text": text
        }

        response = requests.post(url, json=data)
        print(response.json())