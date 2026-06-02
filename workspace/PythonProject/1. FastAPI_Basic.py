# =====================================================
# FastAPI 기본 실습
# - GET 요청 -> 서버 상태 확인
# - POST 요청 -> 사용자 데이터를 받아 처리 후 응답
# =====================================================
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# =====================================================
# 1. Fast API 앱 인스턴스 생성
# =====================================================
# app 객체는 서버의 중심이며, 모든 api 엔드포인트를 여기에 등록함
app = FastAPI(
    title="FastAPI 기본 예제",
    description="PyCharm에서 실습하는 예제",
    version="1.0.0",
)

# =====================================================
# 2. 데이터에 대한 모델 정의(post 요청 시)
# =====================================================
class Item(BaseModel):
    name: str                            # 필수: 아이템 이름
    price: float                   # 필수: 가격
    description: Optional[str] = None    # 선택: 설명

# =====================================================
# 3. 기본 엔드포인트 (get 요청)
# =====================================================
@app.get("/")
def read_root():
    '''
    서버 상태 확인용 기본 엔드포인트
    브라우저나 CURL로 GET 요청시, 메시지 반환
    '''
    return {"message": "FastAPI 서버가 정상적으로 동작 중입니다."}

# =====================================================
# 4. 단순 GET 요청(Query Parameter 사용)
# =====================================================
@app.get("/hello")
def say_hello(name: str='사용자'):
    '''
    get 요청 시, url 파라미터로 이름을 받아 인사 메시지를 반환
    ex) [요청] url/hello?name=홍길동
    '''
    return {"message": f"안녕하세요 {name}님!"}

# =====================================================
# 5. 단순 POST 요청 (Body 데이터 받기)
# =====================================================
@app.post("/items/")
def create_item(item: Item):
    '''
    json 형식의 데이터를 수신하여 서버에서 처리 후 결과 반환
    ex) post 요청 예시
    {
        "name": "노트북",
        "price": 1500000,
        "description": "ai 모델 학습용 고성능 노트북"
    }
    '''
    # 간단한 로직: 부가세 계산
    total_price = item.price * 1.1

    return {
        "name": item.name,
        "description": item.description,
        "price": total_price,
        "message": f"{item.name} 상품이 성공적으로 등록되었습니다."
    }

# =====================================================
# 6. FastAPI 실행(uvicorn)
# =====================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.0.127", port=8000)

