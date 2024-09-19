# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from openai import OpenAI as summaryai
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
# from langchain.prompts import (
#     SystemMessagePromptTemplate,
#     HumanMessagePromptTemplate,
#     ChatPromptTemplate,
#     MessagesPlaceholder
# )

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

    def getConversation_prompttemplate(self, query, reference):
        # 프롬프트 템플릿 설정
        system_message_content = """
        당신은 헬스케어 상담사입니다. CONTEXT의 내용을 바탕으로 Query에 대해 핵심 내용을 먼저 제공한 후, 추가적인 설명을 부드럽게 이어가며 최대 300자 이하로 간략하게 답변해 주세요.
        답변 작성 시 다음 단계를 따라주세요:

        1. CONTEXT만으로 답변이 가능한지 확인해 주세요.
        2. 답변이 어려운 경우, "추가 정보가 필요해요. 예상하시는 추가 정보를 주실 수 있을까요?"라고 요청해 주세요.
        3. 이미 추가 정보를 요청한 경우, "이 질문은 챗봇이 답변하기 어렵습니다. 코치님께 전달드릴게요."라고 안내해 주세요.
        4. CONTEXT가 비어 있거나 질문이 불명확한 경우, "이 질문은 챗봇이 답변하기 어렵습니다. 코치님께 전달드릴게요."라고 답해 주세요.

        답변 작성 지침:
        - CONTEXT에서 Query와 가장 관련된 정보를 두괄식으로 먼저 제공하고, 필요한 추가 설명을 간결하게 덧붙여 주세요.
        - CONTEXT의 말투를 반영해 전문가스럽지만 친근한 말투로 답변해 주세요.
        - 문법적으로 정확한 한국어를 사용해 주세요.
        - 답변은 최대 350자 이하로 작성하고, 글자 수 제한을 엄격히 지켜 주세요.
        - 답변을 부드럽고 이해하기 쉬운 문장으로 마무리해 주세요. 예를 들어, "혈당이 증가하는 원인은 여러 가지가 있을 수 있어요. 기기적 오류가 있을 수도 있고, 첫 끼 식사 후 혈당이 일시적으로 상승할 수도 있답니다."와 같은 방식으로 정보를 제공해 주세요.
        - 전문가와 상담하라는 표현은 지양하고, 가능한 설명만 제공해 주세요.
        - 마지막으로, 답변이 두괄식으로 명확하게 전달되었는지 확인해 주세요. 350자를 초과하면 핵심 내용을 유지하면서 친절한 말투로 요약해 주세요.
        """

        # 메시지 리스트 생성
        messages = [
            SystemMessage(content=system_message_content),
            HumanMessage(content=f"Query: {query}\nCONTEXT: {reference}"),
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
                {
                    "role": "system",
                    "content": f'''
                        사용자의 질문을 읽고, 질문의 요지를 최대 3줄 이내로 간략하게 요약해 주세요.

                        - 질문의 핵심이 하나인 경우: 질문의 요지를 간결하게 한 줄로 요약해 주세요.
                        - 질문에 여러 가지 궁금증이 포함된 경우: 각 궁금증을 최대 3줄 이내로 요약하여 설명해 주세요.
                        - 질문의 맥락이나 중요 포인트를 잘 파악하고, 핵심 정보만을 추출해 주세요.

                        **질문을 요약할 때 고려할 점:**
                        - 사용자가 무엇을 알고 싶어 하는지 명확히 이해해 주세요.
                        - 질문의 배경이나 상황이 중요한 경우, 이를 간단히 설명해 주세요.
                        - 사용자가 질문을 통해 얻고자 하는 구체적인 정보나 도움을 드러내 주세요.

                        형식:
                        - 요지: [간단한 질문에 대한 요약]
                    '''},
                {
                    "role": "user",
                    "content": f'''질문: {query}\n요약: ''',
                },
            ],
            model="gpt-4o",
        )

        summary = chat_completion.choices[0].message.content
        return summary
    
    def summary_add_guid(self, query):
        client = summaryai(
            api_key= os.environ['OPENAI_API_KEY'],
        )
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": f'''
                    사용자의 질문을 읽고, 질문의 요지를 최대 2줄 이내로 간략하게 요약하세요.
                    
                    - 질문의 핵심이 하나인 경우: 요지를 한 줄로 간단히 제공하세요.
                    - 질문에 여러 궁금증이 포함된 경우: 각 포인트를 최대 2줄 이내로 요약하세요.
                    
                    답변 흐름은 다음과 같이 안내하세요:
                    - **기본 원인 설명y**: 질문에 대한 일반적인 원인을 간단히 설명하세요.
                    - **상세 원인 제공**: 추가로 고려해야 할 특정 상황이나 원인을 설명하세요.
                            
                            형식:
                            · 요지: [간단한 한 줄 요약 또는 각 포인트 요약 (최대 2줄)]
                            · 가이드: [답변 흐름에 대한 간략한 단계별 가이드(최대 2줄)]
                '''},
                {
                    "role": "user",
                    "content": f'''질문: {query}\n요약: ''',
                },
            ],
            model="gpt-4o",
        )

        summary = chat_completion.choices[0].message.content
        return summary
    