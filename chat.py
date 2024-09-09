# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from openai import OpenAI as summaryai
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)

# .env 파일 로드
load_dotenv()

class Chatbot_:
    def __init__(self):
        self.llm = ChatOpenAI(
            model_name="gpt-4o", 
            openai_api_key=os.environ['OPENAI_API_KEY'], 
            temperature=0.1,
            max_tokens=500,
            frequency_penalty=0.25, # 반복 감소, 다양성 증가. (0-1)
            presence_penalty=0,  # 새로운 단어 사용 장려. (0-1)
            top_p=0              # 상위 P% 토큰만 고려 (0-1)
        )
        self.mention = " 정보가 부족하여 문서에 기반하지 않고 AI가 생성한 답변입니다."
        
        system_msg_template = SystemMessagePromptTemplate.from_template(
        template=f"""
                    당신은 헬스케어 상담사입니다.
                    CONTEXT의 내용이 없을 경우 스스로 적절한 내용으로 답변하고, CONTEXT의 내용이 있을 경우 참고하여 답변하라.
                    
                    순차적으로 생각한 뒤 답변하라.
                    절대 말을 지어내지 마시오 :
                    1. 사용자의 질문을 이해하기 위해 CoT 방식을 이용하라.
                    2. 답변을 작성할 때 ToT 방식을 사용하라.
                    3. 답변을 작성할 때 ((사용자의 정보가 필요한 질문))에는 원인을 유추하지 말고 "~한 이유는 여러 가지가 있을 수 있어요. 예상하시는 추가정보를 주실 수 있을까요?" 라는 멘트로 답하라: (예시: "혈압이 오른 이유는 여러 가지가 있을 수 있어요. 예상하시는 추가정보를 주실 수 있을까요?", "소화가 잘 안되는 이유는 여러 가지가 있을 수 있어요. 예상하시는 추가정보를 주실 수 있을까요?")
                    4. 이전 답변에서 "~한 이유는 여러 가지가 있을 수 있어요. 예상하시는 추가정보를 주실 수 있을까요?"와 같이 답변했다면, 사용자가 정보를 제공했을 것이다. 사용자가 제공한 정보와 CONTEXT로 답변할 수 없다면 다음과 같이 답하라: {self.mention}
                    5. 사용자의 질문에 CONTEXT만 이용하여 답변을 할 수 있는지 판단하라.
                    6. CONTEXT의 키워드 혹은 가이드만으로 답변을 할 수 있다면, 문법적으로 올바른 한국어 문장으로 답하라.
                    7. ((CONTEXT가 비어있거나, CONTEXT만으로 답변을 생성할 수 없는 경우 혹은 질문에 대한 답을 모르겠는 경우에만)) {self.mention} 라는 멘트와 함께 스스로 적절한 내용을 생성하여 답하라.
                    8. 전문가와 상담하라는 말을 하지 마라.
                    9. 답변 작성 후 문장 단위로 CONTEXT와 일치하는지 다시 한 번 검토하라.
                    10. 각 답변을 작성할 때마다 위의 9가지 지침을 체크리스트로 활용하여 모든 조건을 만족하는지 확인하라.
                    """ 
                    )

        human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")
        self.prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])

    def getConversation_prompttemplate(self, query, reference):
        # 프롬프트 템플릿 설정
        system_message_content = """
            당신은 헬스케어 상담사입니다.
            반드시 CONTEXT의 내용을 참고하여 답변하라.

            0. 사용자의 질문을 이해하기 위해 CoT 방식을 이용하라.
            1. 답변을 작성할 때 ToT 방식을 사용하라.
            2. 답변을 작성할 때 사용자의 정보가 필요한 질문인지 판단하라.
            3. 답변을 작성할 때 사용자의 정보가 필요한 질문에는 원인을 유추하지 말고 "~한 이유는 여러 가지가 있을 수 있어요. 예상하시는 추가정보를 주실 수 있을까요?" 와 같이 사용자가 추가정보를 요구하도록 답하라: (예시: "혈압이 오른 이유는 여러 가지가 있을 수 있어요. 예상하시는 추가정보를 주실 수 있을까요?", "소화가 잘 안되는 이유는 여러 가지가 있을 수 있어요. 예상하시는 추가정보를 주실 수 있을까요?")
            4. CONTEXT만으로 답변을 생성할 수 없고, 답변을 작성할 때 사용자의 정보가 필요하다면 "~한 이유는 여러 가지가 있을 수 있어요. 예상하시는 추가정보를 주실 수 있을까요?" 와 같이 답하라: (예시: "혈압이 오른 이유는 여러 가지가 있을 수 있어요. 예상하시는 추가정보를 주실 수 있을까요?", "소화가 잘 안되는 이유는 여러 가지가 있을 수 있어요. 예상하시는 추가정보를 주실 수 있을까요?")
            5. "~한 이유는 여러 가지가 있을 수 있어요. 예상하시는 추가정보를 주실 수 있을까요?"와 같은 질문을 이전에 했는지 확인하고, CONTEXT을 기반으로 답변할 수 있는지 확인하라. 답변할 수 없다면 더 이상 추가 정보를 물어보지 말고 다음과 같이 답하라: " 해당 질문은 챗봇이 답변하기 어렵습니다. 코치님께 전달드려 답변드리도록 하겠습니다."
            6. CONTEXT가 비어있다면, 다음과 같이 답하라: " 해당 질문은 챗봇이 답변하기 어렵습니다. 코치님께 전달드려 답변드리도록 하겠습니다."
            7. 사용자의 질문에 CONTEXT만을 이용하여 답변을 할 수 있는지 판단하라.
            8. CONTEXT만으로 답변을 생성할 수 없다면 다음과 같이 답변: " 해당 질문은 챗봇이 답변하기 어렵습니다. 코치님께 전달드려 답변드리도록 하겠습니다."
            9. 질문에 대한 답을 모르겠다면 다음과 같이 답변: " 해당 질문은 챗봇이 답변하기 어렵습니다. 코치님께 전달드려 답변드리도록 하겠습니다."
            10. CONTEXT의 키워드와 가이드만으로 답변을 할 수 있다면, 문법적으로 올바른 한국어 문장으로 답변하라.
            11. 절대 CONTEXT에 없는 정보를 추가하지 마라.
            12. 전문가와 상담하라는 말을 하지 마라.
            13. 답변 작성 후 문장 단위로 CONTEXT와 일치하는지 다시 한 번 검토하라.
            14. 각 답변을 작성할 때마다 위의 지침을 체크리스트로 활용하여 모든 조건을 만족하는지 확인하라.
            15. CONTEXT와 비교했을 때 어떠한지에 대해 언급은 하지 마라.

            톤 앤 매너 통일을 위해 아래 요구사항에 맞춰 콘텐츠를 수정하라.
            수정한 콘텐츠만 답하라. 어떻게 수정했는지는 말하지 않음.
            1. 전문가스럽지만, 부드럽고 친근한 말투. (예시: 끝맺음에 "~있어요", "~좋아요" 등을 적절히 섞어 사용)
            2. ((콘텐츠로부터 새로운 내용을 추가하지 않음.))
            3. ((질문으로 끝내지 않음.))
            4. 강한 어조로 단호하게 말하지 않음.
            5. 마무리 멘트 혹은 부가적인 의견을 추가하지 않음.
            6. 문법적으로 올바른 한국어

            User: {input}
            AI:
        """

        # 메시지 리스트 생성
        messages = [
            SystemMessage(content=system_message_content),
            HumanMessage(content=f"질문 : {query}\n참고문서: {reference}"),
        ]
        # OpenAI API 호출
        response = self.llm.invoke(messages)
        return response.content
    
    def summary(self, query):
        client = summaryai(
            api_key= os.environ['OPENAI_API_KEY'],
        )
        
        chat_completion = client.chat.completions.create(
        messages=[
                    {"role": "system", "content": f'''
                        <<<{query}>>>. 
                        앞의 단락은 혈당을 관리하여 살을 빼는 다이어트 프로그램의 참가자가 코치에게 묻는 질문입니다.
                        이 질문의 요지는 무엇인가요?

                        대분류>중분류>소분류 순서로 되어있고, 웰체크 다이어트 사용 안내>사용방법>연속혈당 측정기, 웰체크 다이어트 사용 안내>사용방법>체크리스트, 웰체크 다이어트 사용 안내>사용방법>체성분검사, 웰체크 다이어트 사용 안내>사용방법>자료 링크,
                        웰체크 다이어트 사용 안내>숙명여대 전용>연속혈당측정기 환급, 웰체크 다이어트 사용 안내>숙명여대 전용>디지털휴머니티센터 운영, 웰체크 다이어트 지식>체지방 생성 원리>식단지 식사, 웰체크 다이어트 지식>체지방 생성 원리>식사 순서,
                        웰체크 다이어트 지식>체지방 생성 원리>식초, 웰체크 다이어트 지식>체지방 생성 원리>식후 운동, 웰체크 다이어트 지식>체지방 생성 원리>체지방 생성 원리를 이용한 혈당스파이크 예방법, 웰체크 다이어트 지식>체지방 연소 원리>간헐적 단식,
                        웰체크 다이어트 지식>체지방 연소 원리>숨이 차는 운동, 웰체크 다이어트 지식>혈당 지식>혈당 스파이크, 웰체크 다이어트 지식>혈당 지식>혈당변화-저혈당-고혈당, 웰체크 다이어트 지식>증상 원리>증상 원리, 웰체크 다이어트 지식>증상 원리>수면,
                        웰체크 다이어트 지식>영양소>탄수화물, 웰체크 다이어트 지식>영양소>단백질, 웰체크 다이어트 지식>영양소>지방, 웰체크 다이어트 지식>영양소>비타민-미네랄-물, 웰체크 다이어트 지식>식품>영양성분표-원재료 및 함량, 웰체크 다이어트 지식>식품>식품 선택-추천 식품,
                        웰체크 다이어트 지식>식품>제로칼로리-인공감미료, 기타 건강 지식>기타 건강 지식>인슐린, 기타 건강 지식>기타 건강 지식>케토시스-케토산증-키토래쉬, 기타 건강 지식>기타 건강 지식>식이문제, 기타 건강 지식>기타 건강 지식>근육,
                        기타 건강 지식>기타 건강 지식>체중, 기타 건강 지식>기타 건강 지식>월경-생리, 기타 건강 지식>기타 건강 지식>흡연-음주, 기타 건강 지식>기타 건강 지식>당화반응, 기타 건강 지식>기타 건강 지식>기타, 기타 건강 지식>건강기능식품>건강기능식품, 
                        기타 건강 지식>의약품>당뇨병 치료제, 기타 건강 지식>의약품>비만 치료제, 기타 건강 지식>의약품>기타 약물 이라는 카테고리 중에 이 질문을 해결하기 위해 참고하면 좋을 것 같은 카테고리는 무엇인가요?
                        
                        이 질문에 대하여 아래의 형식을 사용하여 한국말로 대답해주세요.
                        <<< - 요지 : ~
                            - 카테고리 : ~ >>>
                        답변에 특수 기호는 없이 해주세요.
                    "'''},
                    {"role": "user", "content": f'''질문 : {query}\요약: ''',},
                ],
                model="gpt-4o",
        )

        summary = chat_completion.choices[0].message.content
        return summary
    

