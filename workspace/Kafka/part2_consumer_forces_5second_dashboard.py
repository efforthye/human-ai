#========================================================
'''
kafka topic으로 들어오는 센서 데이터를
대시보드(consumer)가 실시간으로 받아서 그래프 시각화 처리한다.

실행 순서
1. part1_producer_10kz.py
2. part2_consumer_force_5second_dashboard.py
'''
#========================================================

from kafka import KafkaConsumer
import json
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt # 시각화 라이브러리
import time
from collections import deque # 데이터 저장

# Consumer 객체 생성
consumer = KafkaConsumer(
    'press-force', # 구독할 데이터를 받아올 topic 이름
    bootstrap_servers=['localhost:9092'], # broker 주소 지정
    auto_offset_reset='latest', # consumer가 처음 실행될 때 최신 데이터로부터 읽도록 설정
    group_id='graph-consumer-group', # consumer 그룹 id 지정 (같은 그룹 id를 가진 consumer는 데이터 나눠서 읽음)
    # Kafka에서 받은 bytes 데이터를 UTF-8 문자열로 바꾸고 JSON을 dict로 변환
    value_deserializer=lambda data: json.loads(data.decode('utf-8'))
)

# 최근 1000개 데이터를 저장 (그래프 5초 단위 실시간 갱신)
MAX_POINTS = 1000
x_data = deque(maxlen=MAX_POINTS)
force_data = deque(maxlen=MAX_POINTS)

# 실시간 모드로 계속 업데이트
plt.ion()
fig, ax = plt.subplots(figsize=(12,6))
line, = ax.plot([], [], linewidth=2)
ax.set_title("Real-Time Press Force Monitoring")
ax.set_xlabel("Sample")
ax.set_ylabel("Press Force")
ax.grid(True)

# 샘플 번호
sample_no = 0
# 마지막 그래프 갱신 시각
last_update = time.time()
# 그래프 갱신 시간 설정 (5초마다 그래프 갱신)
UPDATE_INTERVAL = 5
print(f"5초 단위 그래프 업데이트 시작")

# 그래프 그리기
for message in consumer:
    data = message.value
    sample_no += 1
    force = data['force']

    # 데이터 저장
    x_data.append(sample_no)
    force_data.append(force)
    print(
        f"수신 Sample: {sample_no}, ",
        f"Force: {force}, ",
    )

    # 현재 시간
    current_time = time.time()
    # 5초가 지났는지 확인
    if current_time-last_update >= UPDATE_INTERVAL:
        print("\n=============================\n")
        print(f"{UPDATE_INTERVAL}초 데이터 수집 완료")
        print(f"총 데이터 수: {len(force_data)}")
        print("그래프 업데이트")
        print("\n=============================\n")

        # 그래프 갱신
        line.set_data(
            list(x_data),
            list(force_data)
        )

        # x축 범위 (x축에 출력되는 숫자의 범위 지정)
        ax.set_xlim(min(x_data), max(x_data))
        # y축 범위
        ax.set_ylim(min(force_data)-10, max(force_data)+10)

        # 그래프 다시 그림 (re draw)
        fig.canvas.draw()
        fig.canvas.flush_events()

        # 다음 5초를 측정
        last_update = current_time