# LLM 기반 코치 도우미 추천 답변 생성
Welda 플랫폼의 코칭 업무를 지원하기 위해 설계된 추천 답변 생성 기능을 제공합니다.
Langchain과 LLM(openai API)로 연관 가이드를 연결하고, 이를 통해 사용자 질문에 대해 최적화된 답변을 생성하는 API를 포함합니다.

## 주요 기능
* 질문 요약 및 분석: 입력된 질문을 요약하여 핵심만을 전달합니다.
* 연관 가이드 추천: 질문과 연관된 가이드를 랭킹하여 제공합니다.
* LLM 기반 답변 생성: LLM 및 Langchain을 사용하여 답변을 생성하고 추천합니다.

## API 명세
### Input format
```
{
    "query": "혈당이란 무엇인가요?"
}
```

### Output foramt
| Status Code | 요약 API<br>(Summary API) | 답변 가이드 검색 API<br>(Reference API) | 답변 추천 API<br>(Answer API) |
|:-----------:|:------------------------:|:--------------------------------------:|:-----------------------------:|
| 200         |            O             |                    O                   |               O               |
| 204         |            X             |                    O                   |               X               |
| 403         |            O             |                    O                   |               O               |
| 405         |            O             |                    O                   |               O               |
| 500         |            O             |                    O                   |               O               |
- **200** : 작업 성공, 데이터 반환
- **204** : 작업 성공, 관련 데이터 없음
- **403** : 작업 실패, API 서버 에러
- **405** : 작업 실패, 빈 쿼리 입력
- **500** : 작업 실패, 예상치 못한 에러

---
#### 성공 (200, 204)
- 요약 API
    ```json
    {
        "success": "true",
        "data": [
            {
                "summary": "허리 사이즈 감량 목표 달성을 위한 미션 방법"
            }
        ]
    }
    ```
- 답변 가이드 검색 API
    - 204에서 data는 `[[None, [], []], [None, [], []], ...]`의 형태
    ```json
    {
        "success": "true",
        "data": [
            {
                "reference" : [
                    {
                        "index": 1,
                        "text": "식사 후 발생한 혈당 스파이크는 식곤증을 유발할 수 있습니다.",
                        "keyword" : ["#식곤증" , "#식후졸음"]
                    },
                    ...
                ]
            }
        ]
    }
    ```
- 답변 추천 API
    ```json
    {
        "success": "true",
        "data": [
            {
                "index": [1, 2, 3],
                "reference": ["식사 후 발생한 혈당 스파이크는 식곤증을 유발할 수 있습니다.", "참고문헌2", "참고문헌3"]
            }
        ]
    }
    ```
---
#### 실패
```json
{
    "success": "false",
    "error_code": <STATUS_CODE>,
    "message": "현재 <PROCESS_NAME>이 어렵습니다. 잠시 후에 다시 사용해주세요."
}

```


## ubuntu 서버에서 동작
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
1. 잘못된 가상환경 제거 및 신규 생성
2. Openai API KEY 교체 

2024-10-10
1. 로깅 설정 추가
1) /etc/profile 줄 추가
export PROMPT_COMMAND='RETRN_VAL=$?; logger -t bash -p local1.notice "$(whoami) [$(date +%Y-%m-%d\ %H:%M:%S)] $(history 1 | sed "s/^[ ]*[0-9]\+[ ]*//" )"'
2) /etc/rsyslog.d/50-default.conf 줄 추가
local1.notice    /var/log/cmd.log
3) rsyslog 재시작 : sudo systemctl restart rsyslog

2. 메일링 설정
1) /home/ubuntu/send_ssh_log.sh 생성
2) crontab -e 줄 추가 : * * * * * /home/ubutu/send_ssh_log.sh
3) 외부 stmp 서버 설정 (hostname -f : ip-172-31-50-136.ap-northeast-2.compute.internal)
4) /etc/postfix/main.cf 변경 : relayhost설정, TLS 설정 추가
5) /etc/postfix/sasl_passwd : 계정정보 추가 후 적용
sudo vim /etc/postfix/main.cf
sudo postmap /etc/postfix/sasl_passwd
sudo systemctl restart postfix
6) 테스트 : echo "Test email content" | mail -s "Test Subject" test@test.com
tail -n /var/log/auth.log
tail -f /var/log/mail.log