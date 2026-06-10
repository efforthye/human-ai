# 아나콘다 제거
- 제어판, 프로그램, 프로그램 및 기능 -> 아나콘다 삭제

# 아나콘다 가상환경 설치
1. Anaconda 설치 
  : https://www.anaconda.com/download/success
    - Window Distribution Installers 다운

2. 가상환경 설치 - 설치된 아나콘다 폴더의 아나콘다 프롬프트로 진행.
  # pip 업그레이드
     >> python -m pip install --upgrade pip
  # conda 가상 환경 (ai=아이디명)
     >> conda create -n ai python=3.10   
     >> conda info --envs (가상환경 설치 확인)
  # 가상환경 활성화
     >> activate ai

3. 분석 라이브러리 설치
    - pip install matplotlib //시각화
    - pip install seaborn  //시각화
    - pip install numpy // 데이터처리
    - pip install pandas // 데이터 처리
    - pip install scikit-learn // 분석
    - pip list <--설치버전확인

4. Jupyter notebook 설치
    >> conda install jupyter notebook 

* 가상환경 conda 확인 및 삭제
       - conda info --envs /*아나콘다 환경 확인하기*/
       - conda remove --name 삭제하려는환경이름 --all /*아나콘다 환경 삭제하기*/


-Window 트레이에서 anaconda3>jupyter notebook(생성한 id명) 실행
-바탕화면에 workspace 폴더 생성하고, jupyter notebook에서 해당 경로
에서 파이썬 파일 생성

# 몽고디비 설치
```
=============================================
## MongoDB 설치 ##
=============================================

# 다운로드
  - “”접속
  - Windows Installer(.msi) 다운로드
    >> More Option > Archived releases > Msi: mongodb-windows-x86_64-5.0.33-signed.msi


# 설치 과정
  - “Complete” 설치 선택
  - 기본설치 경로 : C:\Program Files\MongoDB\Server\<버전>\bin
  - “Install MongoDB as a Service” 체크
  - “MongoDB Compass” 설치 선택 가능 (GUI 기반 MongoDB 관리 툴)


=============================================
## 환경 변수 설정 ##
=============================================

# 탐색기에서:
C:\Program Files\MongoDB\Server\<버전>\bin 경로 복사

# 시스템 환경 변수 편집:

# Windows 검색 → 환경 변수 → 시스템 환경 변수 편집

# 시스템 변수 영역의 Path 선택 → 편집

# 새로 만들기 → MongoDB bin 경로 붙여넣기 → 확인
                       : C:\Program Files\MongoDB\Server\<버전>\bin

=============================================
## 설치 확인 ##
=============================================

# 터미널 재실행 후 설치 확인
   > mongod --version
   > mongo --version

# 데이터 저장 폴더 생성 (기본적으로 해당 경로 이용)
   > mkdir C:\data\db

   * 데이터 폴더 경로 직접 지정하는 경우
   > mongod --dbpath C:\data\db

# MongoDB 서버 실행
   > mongod
```