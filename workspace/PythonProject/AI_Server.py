# ====================================================
# TCP/IP 서버 실습
'''
클라이언트가 이미지를 보내면 Tensorflow 모델로 분류 후
결과를 클라이언트에 반환하는 AI 서버 구현
'''
# ====================================================
import socket
import struct
import json
import numpy as np
import tensorflow as tf
from PIL import Image   # 이미지 처리
from io import BytesIO  # 메모리 상의 이미지 처리

## 인퍼런스 추론 모듈 만들기 (AI 추론 모듈 개발 -> 서버 역할)

# ====================================================
# CIFAR10 클래스 정의
# ====================================================
CLASS_NAMES = [
    "airplane",
    "automobile",
    "bird",
    "cat",
    "deer",
    "dog",
    "frog",
    "horse",
    "ship",
    "truck",
]

# ====================================================
# 학습 모델 결과 로드
# ====================================================
print("AI 모델 로딩 시작")

# 모델 읽어오기
model = tf.keras.models.load_model("./model/cifar10_model.h5")
print(f"AI 모델 로딩 완료")

# ====================================================
# 지정 크기만큼 데이터 수신 함수 (데이터 받아오기)
# (클라이언트에서 이미지 데이터를 주면 이미지를 처리한 후
# 해당 이미지를 가지고 분류 -> receive 데이터에 대해 처리)
# ====================================================
def recv_all(sock, size):
    data = b''
    # 이미지는 데이터 바이트스트링으로 보내주는데 5000바이트이면 2000바이트
    # 이런 식으로 순서대로 주기 때문에 계속 순차적으로 받아서 처리하기 위해 while 문을 사용
    while len(data) < size:
        packet = sock.recv(size - len(data))
        if not packet:
            return None
        data += packet

    return data

# ====================================================
# [인퍼런스 추론 모듈]
# 이미지 데이터에 대해 추론을 하는 함수 구현
# - 서버는 이미지를 바이트로 받아서 이미지로 변환하고
# 변환된 이미지를 기반으로 추론을 진행한다.
# ====================================================
def predict_image(image_bytes):
    # 바이트를 이미지로 오픈
    image = Image.open(BytesIO(image_bytes))
    # RGB 형태로 변환
    image = image.convert("RGB")
    # CIFAR10(32x32 컬러 이미지) 사이즈에 맞춤
    image = image.resize((32, 32))
    # 추론을 위해 numpy 배열로 변환
    image = np.array(image)
    # numpy 배열로 변환한 것을 정규화
    image = image / 255.0
    # 배치 차원 추가
    image = np.expand_dims(image, axis=0)
    print(f"입력 shape: {image.shape}")

    # [중요] 모델 추론
    # 추론을 위해서는 추론을 하기 위해서 신규 데이터를 받으면
    # 학습 했었던 전처리와 피쳐 뽑는 것을 동일하게 진행 후 해야한다.

    # 모델 추론 결과를 pred 변수에 저장
    pred = model.predict(image, verbose=0)

    # 예측 결과 출력
    print(f"예측 확률")
    print(pred)

    # 10개에 대한 모든 클래스에 대해 예측 확률값을 계산한다.
    # 거기에 대해 가장 높은 확률을 결과로 리턴한다.

    # 가장 높은 확률 결과 리턴
    # argmax 방식 = 소프트맥스 기반. 가장높은 확률값을 1로 치환하고 나머지를 0으로 치환함.
    class_idx = np.argmax(pred)
    confidence = pred[class_idx]
    print(f"예측 클래스: {class_idx}")
    print(f"신뢰도: {confidence}({confidence * 100}%)")

    # 결과 생성
    result = {
        "class_id": int(class_idx),
        "class_name": CLASS_NAMES[class_idx],
        "confidence": float(confidence),
    }

    return result


# ====================================================
# [서버 설정]
# ====================================================