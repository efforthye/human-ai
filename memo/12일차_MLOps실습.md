# MLOps 실습 전체 시나리오
- 시나리오 1: 모델 학습(train.py)
- 시나리오 2: FastAPI 예측 서버 + Drift 감지(app.py)
- 시나리오 3: Drift 발생 시 자동 재학습(train_retrain.py)
- 시나리오 4: 모델 변경 감지 및 FastAPI 자동 재시작(watch_reload.py)
- 시나리오 5: Docker + Docker Compose 기반 MLOps 통합 실행(Dockerfile / docker-compose.yml)

~/mlops-practice/
│ train.py
│ app.py
│ train_retrain.py
│ watch_reload.py
│ Dockerfile
│ docker-compose.yml
________________________________________
[시나리오 1] 모델 최초 학습(train.py)
목적
•	기본 모델(RandomForestClassifier) 학습
•	model.pkl 파일 생성
•	Drift 기준(reference) 데이터 저장
________________________________________
train.py 
"""
train.py
- 최초의 학습 데이터로 모델을 학습하고 model.pkl로 저장
- 학습 데이터 분포(reference.npy)를 저장하여 drift 감지 기준으로 사용
"""

import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------
# 1. 학습 데이터 생성
# ---------------------------------------------------------
# 정규분포를 따르는 실수 데이터 200개 생성
X = np.random.randn(200,1)

# threshold(0)를 기준으로 이진 라벨 생성
y = (X[:,0] > 0).astype(int)

# ---------------------------------------------------------
# 2. 모델 학습
# ---------------------------------------------------------
model = RandomForestClassifier()
model.fit(X, y)

# ---------------------------------------------------------
# 3. 학습된 모델과 레퍼런스 데이터 저장
# ---------------------------------------------------------
joblib.dump(model, "model.pkl")      # 모델 저장
np.save("reference.npy", X)          # 학습 당시 데이터 분포 저장

print("✔ 모델 학습 완료: model.pkl / reference.npy 생성됨")

# ---------------------------------------------------------
# 4. 학습 데이터 분포 시각화
# ---------------------------------------------------------
# 데이터 로드
reference = np.load("reference.npy")

# 분포 시각화
plt.figure(figsize=(10,5))

# 히스토그램 + KDE
sns.histplot(reference[:,0], bins=30, kde=True)

plt.title("📊 Reference Data Distribution (Training Data)")
plt.xlabel("Feature Value")
plt.ylabel("Frequency")

plt.grid()
plt.show()
________________________________________
▶ 실행 명령어
python train.py
________________________________________
✔ 실행 결과 해석
폴더에 다음 파일이 생성됨:
•	model.pkl → 예측 모델
•	reference.npy → Drift 비교 기준
터미널 출력:
✔ 모델 학습 완료: model.pkl / reference.npy 생성됨
________________________________________
________________________________________
[시나리오 2] FastAPI 예측 서버 + Drift 감지(app.py)
목적
•	/predict API에서 실시간 예측 수행
•	요청 값 누적 (incoming)
•	50개 이상 쌓이면 KS-test로 Drift 감지
•	drift_detected=True이면 incoming.npy 저장
•	자동 재학습(tran_retrain.py) 트리거
________________________________________
app.py 
"""
app.py
- FastAPI 실시간 예측 API
- 요청 데이터 누적 후 KS-test 기반 drift 감지
- drift 발생 시 incoming.npy 저장 및 자동 재학습 트리거
"""

from fastapi import FastAPI
import numpy as np
import joblib
from scipy.stats import ks_2samp
import subprocess

app = FastAPI()

# ---------------------------------------------------------
# 1. 모델과 기준(reference) 데이터 로드
# ---------------------------------------------------------
model = joblib.load("model.pkl")
reference = np.load("reference.npy").ravel()   # KS-test 용 1차원 데이터
incoming = []  # 운영 데이터 누적 리스트

# ---------------------------------------------------------
# 2. 예측 엔드포인트
# ---------------------------------------------------------
@app.get("/predict")
def predict(value: float):
    """
    입력된 value 값에 대해 예측을 수행하고,
    incoming 데이터를 누적하여 drift 여부를 반환한다.
    """

    incoming.append(value)

    drift_detected = False  # 기본값

    # ---------------------------------------------------------
    # Drift 감지: 50개 이상 쌓이면 KS-test 수행
    # ---------------------------------------------------------
    if len(incoming) > 50:
        stat, p = ks_2samp(reference, incoming)
        drift_detected = bool(p < 0.05)  # numpy.bool → python bool 변환

        if drift_detected:
            print(" Drift 감지 → incoming.npy 저장")
            np.save("incoming.npy", np.array(incoming))

            # 자동 재학습 프로세스 실행
            subprocess.Popen(["python3", "train_retrain.py"])

    # ---------------------------------------------------------
    # 모델 예측 수행
    # ---------------------------------------------------------
    pred = model.predict([[value]])  # 입력 shape(1,1) 유지 필수

    return {
        "value": value,
        "prediction": int(pred[0]),
        "drift_detected": drift_detected,
        "sample_size": len(incoming)
    }
________________________________________
▶ 실행 테스트
서버 실행
: uvicorn app:app --host 0.0.0.0 --port 8000

** incoming 데이터가 0과 1 두 클래스 모두 포함되도록 입력을 넣어야
정상 데이터(드리프트 없음): 레이블 1
for i in $(seq 1 40); do curl "http://localhost:8000/predict?value=0.1"; echo; done
for i in $(seq 1 10); do curl "http://localhost:8000/predict?value=10"; echo; done

이상 데이터(Drift 유도 음수데이터 추가): 레이블 0
for i in $(seq 1 20); do curl "http://localhost:8000/predict?value=-5"; echo; done
________________________________________
✔ 결과 해석
Drift 발생하면 API 응답:
"drift_detected": true
터미널 로그:
 Drift 감지 → incoming.npy 저장
________________________________________
________________________________________
[시나리오 3] Drift 발생 시 자동 재학습(train_retrain.py)
목적
•	incoming.npy 기반으로 재학습
•	단일 클래스(class=1만 존재 등)일 경우 오류 방지
•	재학습된 model.pkl 업데이트
________________________________________
train_retrain.py 
"""
train_retrain.py
- Drift 발생 후 저장된 incoming.npy로 재학습 수행
- 단일 클래스 데이터일 경우 재학습 생략하여 오류 방지
"""

import numpy as np
import joblib
from sklearn.linear_model import LogisticRegression

print(" 재학습 시작")

# ---------------------------------------------------------
# 1. incoming 데이터 로드
# ---------------------------------------------------------
incoming = np.load("incoming.npy")
X = incoming.reshape(-1, 1)           # 2차원으로 변환
y = (X[:,0] > 0).astype(int)          # threshold 기반 라벨 생성

# ---------------------------------------------------------
# 2. 단일 클래스 여부 체크
# ---------------------------------------------------------
unique_classes = np.unique(y)
print("incoming 데이터 클래스:", unique_classes)

if len(unique_classes) < 2:
    print("단일 클래스 → 재학습 스킵")
    exit(0)

# ---------------------------------------------------------
# 3. 모델 재학습
# ---------------------------------------------------------
model = LogisticRegression()
model.fit(X, y)

# ---------------------------------------------------------
# 4. 새로운 모델 저장
# ---------------------------------------------------------
joblib.dump(model, "model.pkl")

print(" 재학습 완료 → model.pkl 업데이트됨")
________________________________________
✔ 결과 해석
(1) 단일 클래스일 때
incoming 데이터 클래스: [1]
 단일 클래스 → 재학습 스킵
기존 모델 유지
(2) 다중 클래스일 때
incoming 데이터 클래스: [0 1]
재학습 완료 → model.pkl 업데이트됨
이후 시나리오 4에서 자동 reload 발생
________________________________________
________________________________________
[시나리오 4] 모델 변경 감지 → FastAPI 자동 Reload(watch_reload.py)
목적
•	model.pkl이 변경되면
o	FastAPI 서버 자동 재시작
o	자동 재배포 효과
________________________________________
watch_reload.py 
"""
watch_reload.py
- model.pkl 파일의 수정시간(mtime)을 모니터링
- 변경되면 FastAPI 서버를 자동 재시작하여 새로운 모델 즉시 반영
"""

import os
import time
import subprocess

MODEL_FILE = "model.pkl"

# ---------------------------------------------------------
# model.pkl의 수정 시간 반환 함수
# ---------------------------------------------------------
def get_ts():
    return os.path.getmtime(MODEL_FILE)

print("model.pkl 변경 감지 시작")

last_ts = get_ts()

# ---------------------------------------------------------
# FastAPI 최초 실행
# ---------------------------------------------------------
process = subprocess.Popen([
    "uvicorn", "app:app",
    "--host", "0.0.0.0",
    "--port", "8000"
])

# ---------------------------------------------------------
# 파일 변경 감지 루프
# ---------------------------------------------------------
while True:
    time.sleep(1)
    new_ts = get_ts()

    if new_ts != last_ts:  # 변경됨
        print("model.pkl 변경 감지 → FastAPI 재시작")

        process.kill()
        process = subprocess.Popen([
            "uvicorn", "app:app",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])

        last_ts = new_ts
        print("✔ FastAPI 재시작 완료 (새 모델 적용됨)")
________________________________________
▶ 실행
python watch_reload.py
________________________________________
✔ 결과 해석
모델이 업데이트되면:
 model.pkl 변경 감지 → FastAPI 재시작
 FastAPI 재시작 완료 (새 모델 적용됨)
재학습 후 즉시 새 모델로 서비스됨
________________________________________
________________________________________
[시나리오 5] Docker + Docker Compose 통합 실행
이 부분이 현업 MLOps와 동일한 구조입니다.
________________________________________
Dockerfile 
# ---------------------------------------------------------
# FastAPI + 모델 파일을 포함한 MLOps 컨테이너 이미지
# ---------------------------------------------------------

FROM python:3.10

# 필요한 라이브러리 설치
RUN pip install fastapi uvicorn scikit-learn joblib scipy

# 프로젝트 파일 복사
COPY app.py /app/app.py
COPY train_retrain.py /app/train_retrain.py
COPY train.py /app/train.py
COPY model.pkl /app/model.pkl
COPY reference.npy /app/reference.npy
COPY watch_reload.py /app/watch_reload.py

WORKDIR /app

# FastAPI 자동 reload 방식으로 실행 (watch_reload 사용)
CMD ["python3", "watch_reload.py"]
________________________________________
docker-compose.yml 
version: "3.8"

services:
  mlops-api:
    build: .
    container_name: mlops-fastapi
    ports:
      - "8000:8000"     # FastAPI 포트
    volumes:
      - .:/app          # model.pkl 변경 시 즉시 반영
    restart: always
________________________________________
▶ Docker 기반 전체 실행 흐름
1 이미지 빌드
docker build -t mlops/api:v1 .
________________________________________
2 컨테이너 실행
docker-compose up 
________________________________________
3 예측 요청
curl "http://localhost:8000/predict?value=0.5"
________________________________________
4 drift 유도
for i in $(seq 1 60); do curl "http://localhost:8000/predict?value=10"; echo; done
- drift 감지
- incoming.npy 저장
- train_retrain.py 자동 실행
- model.pkl 업데이트
- FastAPI 자동 reload
- 컨테이너 내부에서도 자동 반영됨
________________________________________
전체 실습 흐름 요약 
1.	train.py
o	모델 최초 학습
o	model.pkl + reference.npy 생성
2.	app.py
o	예측 수행
o	drift 감지
o	drift 발생 시 자동 재학습 트리거
3.	train_retrain.py
o	incoming.npy 기반 재학습
o	model.pkl 업데이트
4.	watch_reload.py
o	model.pkl 변경 감지 → FastAPI 재시작
5.	Docker Compose
o	모든 기능을 하나의 서비스로 통합 실행
o	모델 변경 → 자동 재배포
o	완전한 MLOps 실습 구성 완성

