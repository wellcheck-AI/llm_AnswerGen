# LLM 기반 코치 도우미 추천 답변 생성
Welda 플랫폼의 코칭 업무를 지원하기 위해 설계된 추천 답변 생성 기능을 제공합니다.
Langchain과 LLM(openai API)로 연관 가이드를 연결하고, 이를 통해 사용자 질문에 대해 최적화된 답변을 생성하는 API를 포함합니다.

## 주요 기능
* 질문 요약 및 분석: 입력된 질문을 요약하여 핵심만을 전달합니다.
* 연관 가이드 추천: 질문과 연관된 가이드를 랭킹하여 제공합니다.
* LLM 기반 답변 생성: LLM 및 Langchain을 사용하여 답변을 생성하고 추천합니다.

## 실행
가상환경 실행 (requirements.txt 설치된 상태)
```
source .venv/bin/activate
```

API 엔드포인트 앱 실행
```
nohup python3 app.py > output.log 2>&1 &
```

프로세스 확인
```
ps aux | grep app.py
```

테스트코드 실행
```
python3 api_test.py
```

## 변경사항
2024-09-06
1. 서치 코드 변경
Deberta 모델을 제거하고, OpenAI API를 사용한 새로운 서치 로직으로 대체, 키워드 서치 & Rerank 기능 관련 제거, 추천 답변 생성 코드 수정
2. 의존성
Langchain 호출 경로를 최신 버전 업데이트, ChatOpenAI 파라미터 수정

2024-09-09
1. Openai API KEY 교체 
