#=====================================================
'''
producer가 0.1초마다 데이터 전송
consumer가 초당 약 10건 수신 => tps 출력

순서: consumer 실행 --> producer 실행
'''
#=====================================================

from kafka import KafkaConsumer
import json
import time

# kafka consumer 객체 생성
consumer = KafkaConsumer(
    'press-force', # 토픽 네임 producer와 맞춰야 함
    bootstrap_servers=['localhost:9092'], # broker 주소
    auto_offset_reset='latest', # 최근 데이터
    group_id='tps-consumer-group', # consumer 그룹 id 지정 (같은 그룹 id를 가진 consumer는 데이터 나눠서 읽음)
    # Kafka에서 받은 bytes 데이터를 UTF-8 문자열로 바꾸고 JSON을 dict로 변환
    value_deserializer=lambda data: json.loads(data.decode('utf-8'))
)

# 1초 동안 수신한 메시지 개수를 저장
count_per_second = 0

# 프로그램 시작 후 전체 수신한 메시지 개수를 저장
total_count = 0

# TPS 측정 시작 시간을 저장
start_time = time.time()

# consumer 시작 메시지 출력
print(f"TPS Consumer 시작: 초당 수신 건수를 계산합니다.")

# kafka topic 에서 메시지를 계속 읽어오기
for message in consumer:
    data = message.value
    count_per_second += 1 # 1초 단위 카운터 1씩 증가
    total_count += 1 # 전체 누적 카운터 1씩 증가
    current_time = time.time() # 현재 시간 가져옴

    if current_time - start_time > 1.0:
        # 최근 1초동안 수신한 메시지 개수를 tps로 출력
        print(
            f"현재 TPS: {count_per_second} 건/초, ",
            f"누적 수신: {total_count} 건, "
            f"최근 force: {data['force']}"
        )
        count_per_second = 0 # 1초 단위 카운터 초기화
        start_time = current_time # TPS 측정 시작 시간 현재 시간으로 갱신


