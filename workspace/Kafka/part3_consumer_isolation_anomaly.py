# ============================================================
'''
producer -> topic(press-force) -> isolation forest consumer
-> normal or anmaly 판단 -> 이상 탐지 결과 실시간 그래프 출력

실행 순서
1. part1_producer_10hz.py
2. part3_consumer_isolation_anomaly.py
'''
# ============================================================

from kafka import KafkaConsumer

import json
import time
import numpy as np
from sklearn.ensemble import IsolationForest

import matplotlib.pyplot as plt
import signal
import sys

## kafka consumer 객체 생성
consumer = KafkaConsumer(
    "press-force",                          # 구독하기 위한 토픽
    bootstrap_servers=['localhost:9092'],   # 카프카 브로커 주소
    auto_offset_reset='latest',             # 최신 데이터부터 읽어오기
    group_id='isolation-visual-group',      # consumer group
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))  # bytes -> dict 변환
)

# 학습 설정
TRAIN_SIZE = 100   # 학습시킬 데이터 단위(프로듀서에서 보내는 데이터 개수)
train_data = []    # 학습 데이터 저장
model = None       # AI 모델

# 결과 저장
all_force = []     # 전체 force 저장
all_status = []    # normal/anomaly 저장
all_index = []     # 샘플 번호 저장

# threshold 기준 정의 (지금은 임의로 지정)
THRESHOLD = 170

# 그래프 설정
plt.ion()  # 인터랙티브 모드 on (실시간 갱신용)
fig, ax = plt.subplots(figsize=(14, 7))

# 그래프 갱신 주기 (10초)
UPDATE_INTERVAL = 10

# 마지막 갱신 시각
last_update_time = time.time()

# 실시간 그래프 갱신 함수
def update_graph():
    ax.clear()

    # Force 시계열
    ax.plot(
        all_index,
        all_force,
        linewidth = 2,
        color = 'blue',
        label = 'Force',
    )

    # threshold
    ax.axhline(
        y = THRESHOLD,
        color = 'orange',
        linestyle = '--',
        linewidth = 2,
        label = f'Threshold={THRESHOLD}',
    )

    # 이상 데이터 추출
    anomaly_x = []
    anomaly_y = []
    for idx, force, status in zip(all_index, all_force, all_status):
        if status == 'ANOMALY':
            anomaly_x.append(idx)
            anomaly_y.append(force)

    # 이상 데이터 표시
    ax.scatter(
        anomaly_x,
        anomaly_y,
        color = 'red',
        s = 100,
        marker = 'o',
        label = 'AI Anomaly',
    )

    # 그래프 설정
    ax.set_title("kafka + Isolation Forest Anomaly Detection")
    ax.set_xlabel("Sample")
    ax.set_ylabel("Force")
    ax.grid(True)
    ax.legend()
    plt.tight_layout()

    # 화면 강제 갱신
    fig.canvas.draw()
    fig.canvas.flush_events()

# 최종 결과 시각화 함수
def show_final_result():
    print("\n최종 결과 그래프 생성\n")
    plt.figure(figsize=(14, 7))

    # Force 시계열
    plt.plot(
        all_index,
        all_force,
        linewidth = 2,
        label = 'Force',
    )

    # threshold 표시
    plt.axhline(
        y = THRESHOLD,
        color = 'orange',
        linestyle = '--',
        linewidth = 2,
        label = f'Threshold={THRESHOLD}',
    )

    # 이상 데이터 추출
    anomaly_x = []
    anomaly_y = []
    for idx, force, status in zip(all_index, all_force, all_status):
        if status == 'ANOMALY':
            anomaly_x.append(idx)
            anomaly_y.append(force)

    # 이상 데이터 표시 (그래프로 결과 뽑기)
    plt.scatter(
        anomaly_x,
        anomaly_y,
        color = 'red',
        s = 100,
        marker = 'o',
        label = 'AI Anomaly',
    )
    plt.title("kafka + Isolation Forest Anomaly Detection")
    plt.xlabel("Sample")
    plt.ylabel("Force")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

# Ctrl+C 처리 함수
def signal_handler(sig, frame):
    print("\n프로그램 종료")

    # 최종 그래프 한번 더 그림
    update_graph()

    # 실시간 모드 종료
    plt.ioff()

    # 최종 그래프 유지
    plt.show()

    sys.exit(0)

# 실행
if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)

    print("IsolationForest Consumer 시작")
    sample_no = 0

    # kafka 데이터 수신
    for message in consumer:
        data = message.value     # kafka 데이터
        sample_no += 1           # 샘플 번호
        force = data["force"]    # force 값

        # 저장
        all_index.append(sample_no)
        all_force.append(force)

        # AI 입력
        x = np.array([[force]])

        # 모델 학습 전
        if model is None:
            train_data.append([force])
            print(f"학습 데이터 수집중 {len(train_data)}/{TRAIN_SIZE}")

            # 100개 모이면 학습
            if len(train_data) >= TRAIN_SIZE:
                model = IsolationForest(
                    contamination = 0.05,
                    random_state = 42,
                )
                model.fit(np.array(train_data))
                print("\nAI 모델 학습 완료\n")

            continue

        # 예측
        pred = model.predict(x)

        # 결과 판정 (isolation -1 이상 / 1 정상)
        if pred[0] == -1:
            status = "ANOMALY"
        else:
            status = "NORMAL"

        # 결과 저장
        all_status.append(status)

        # 콘솔 출력
        print(f"Force={force:.2f}, Result={status}")

        # 10초마다 그래프 자동 갱신
        current_time = time.time()
        if current_time - last_update_time >= UPDATE_INTERVAL:
            print("\n===== 그래프 갱신 =====\n")
            update_graph()
            last_update_time = current_time