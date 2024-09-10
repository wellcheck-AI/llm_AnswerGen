#!/bin/bash

# 로그 파일 경로
LOGFILE="/var/log/auth.log"  # Ubuntu 기반. CentOS/Red Hat은 /var/log/secure 사용
SEARCH_PATTERN="Accepted"  # SSH 접속 성공 패턴
LAST_LOG="/tmp/last_ssh_log"  # 마지막으로 확인한 로그 저장 파일

# 마지막으로 확인한 줄 번호를 저장하는 파일이 없으면 생성
if [ ! -f $LAST_LOG ]; then
  echo 0 > $LAST_LOG
fi

LAST_LINE=$(cat $LAST_LOG)  # 마지막 확인한 로그 줄 번호 읽기
CURRENT_LINE=$(wc -l < $LOGFILE)  # 현재 로그 파일의 총 줄 수

if [ $LAST_LINE -lt $CURRENT_LINE ]; then
  # 새로운 로그 부분에서 "Accepted" 메시지가 있는지 확인하고 이메일로 바로 전송
  tail -n $((CURRENT_LINE - LAST_LINE)) $LOGFILE | grep "$SEARCH_PATTERN" | mail -s "New SSH Connection Detected" dyk43e@daewoong.co.kr
  
  # 현재 로그의 마지막 줄 번호 업데이트
  echo "$CURRENT_LINE" > $LAST_LOG
fi

