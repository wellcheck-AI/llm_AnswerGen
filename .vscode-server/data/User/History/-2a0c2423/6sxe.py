import os
import json
import tiktoken
from flask import Flask, jsonify, request
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from dotenv import load_dotenv
from utils import *
from document import Document_
from chat import Chatbot_
from flasgger import Swagger  # 추가

openai_api_key = "sk-proj-b6qcVgzDgacMtTrObcKvT3BlbkFJjM4ZbjkRvlFTeBa6ZsoP"
cohere_api_key = "unoKJ0fmAD5yqqF5xYCWwcO4a8CFXPxwAXJOXm9N"
pinecone_api = "24c94c01-5774-42cf-a92f-bf969b18d5a7"

os.environ['OPENAI_API_KEY'] = openai_api_key
os.environ['COHERE_API_KEY'] = cohere_api_key
os.environ['pinecone_api'] = pinecone_api

def encoding_getter(encoding_type:str):
    return tiktoken.encoding_for_model(encoding_type)
            
def tokenizer(string:str, encoding_type:str)->list:
    encoding = encoding_getter(encoding_type)
    tokens=encoding.encode(string)
    return tokens
            
def token_counter(string:str, encoding_type:str) -> int:
    num_tokens = len(tokenizer(string, encoding_type))
    return num_tokens
            
load_dotenv()

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSON_AS_ASCII'] = False

swagger = Swagger(app, config={
    'swagger_ui': True,
    'specs_route': '/docs/',
    'specs': [
        {
            'endpoint': 'apispec_1',
            'route': '/docs/apispec_1.json',
            'rule_filter': lambda rule: True,  # 모든 경로를 포함
            'model_filter': lambda tag: True,  # 모든 태그를 포함
        }
    ]
})

llm = Chatbot_()
document = Document_()

@app.route('/')
def index():
    return "Hello"

@app.route('/summary', methods=['POST'])
def summary():
    """
    Summarize a given query using the LLM.
    ---
    parameters:
      - name: query
        in: body
        type: string
        required: true
        description: The query to be summarized.
    responses:
      200:
        description: A summary of the query.
      400:
        description: Error occurred while processing the query.
      500:
        description: Server error.
    """
    try:
        data = request.json
        query = data['query']

        try:
            summary = llm.summary(query)
        except:
            raise ValueError("OpenAI 호출 실패")

        response = {
                    "success" : "true",
                    "data" : [
                        {
                            "summary" : summary,
                        }
                    ]
                }

    except ValueError as e:
        response = {
                    "success" : "false",
                    "error_code" : 400,
                    "message" : "현재 AI 질문 요약이 어렵습니다. 잠시 후에 다시 사용해주세요."
                }
        response = json.dumps(response, ensure_ascii=False)

    except Exception as e:
        response = {
                    "success" : "false",
                    "error_code" : 500,
                    "message" : "현재 AI 질문 요약이 어렵습니다. 잠시 후에 다시 사용해주세요."
                }
        response = json.dumps(response, ensure_ascii=False)
        
    return jsonify(response)

@app.route('/reference', methods=['POST'])
def reference():
    """
    Get references for a given query.
    ---
    parameters:
      - name: query
        in: body
        type: string
        required: true
        description: The query to find references for.
    responses:
      200:
        description: A list of references related to the query.
      400:
        description: Error occurred while processing the query.
      500:
        description: Server error.
    """
    try:
        data = request.json
        query = data['query']

        try:
            buffer_memory = ConversationBufferWindowMemory(k=3, return_messages=True)
            conversation = llm.getConversation_chatprompttemplate(buffer_memory)
            context = document.find_match_(document.query_refine(buffer_memory,query))
        except:
            raise ValueError("OpenAI 호출 실패")
                
        reference = {
            "reference": []
        }

        for i, c in enumerate(context, start=1):
            reference["reference"].append({
                "index": c[0],
                "keyword": c[1],
                "text": c[2][0],
            })
                
        response = {
                    "success" : "true",
                    "data" : [
                        reference
                    ]
                }

    except ValueError as e:
        response = {
                    "success" : "false",
                    "error_code" : 400,
                    "message" : "현재 AI 질문 요약이 어렵습니다. 잠시 후에 다시 사용해주세요."
                }
        response = json.dumps(response, ensure_ascii=False)

    except Exception as e:
        response = {
                    "success" : "false",
                    "error_code" : 500,
                    "message" : "현재 AI 질문 요약이 어렵습니다. 잠시 후에 다시 사용해주세요."
                }
        response = json.dumps(response, ensure_ascii=False)
        
    return jsonify(response)

@app.route('/answer', methods=['POST'])
def answer():
    """
    Provide an answer based on the query and provided context.
    ---
    parameters:
      - name: query
        in: body
        type: string
        required: true
        description: The query to be answered.
      - name: data
        in: body
        type: object
        required: true
        description: The data containing references to be used for answering the query.
    responses:
      200:
        description: The generated answer.
      400:
        description: Error occurred while processing the query.
      500:
        description: Server error.
    """
    try:
        json_data = request.json

        query = json_data['query']
        index_list = json_data['data'][0]['index']
        reference_list = json_data['data'][0]['reference']

        context = '\n'.join(reference_list)
        context = document.context_to_string(context, query)

        try:
            buffer_memory = ConversationBufferWindowMemory(k=3, return_messages=True)
            conversation = llm.getConversation_prompttemplate(buffer_memory)
            
            answer = conversation.predict(input=f"Context:{context}\nQuery:{query}\nAnswer:")
                    
            answer = "(자동화된 답변) " + llm.llm.predict(text=f"""콘텐츠 : {answer}
                                톤 앤 매너 통일을 위해 아래 요구사항에 맞춰 콘텐츠를 수정하라.
                                수정한 콘텐츠만 답하라. 어떻게 수정했는지는 말하지 않음.
                                요구사항
                                1. 전문가스럽지만, 부드럽고 친근한 말투. (예시: 끝맺음에 "~있어요", "~좋아요" 등을 적절히 섞어 사용)                                
                                2. ((콘텐츠로부터 새로운 내용을 추가하지 않음.))
                                3. ((질문으로 끝내지 않음.))
                                4. 강한 어조로 단호하게 말하지 않음.
                                5. 마무리 멘트 혹은 부가적인 의견을 추가하지 않음.
                                6. 문법적으로 올바른 한국어
                                수정된 콘텐츠 : """)

        except:
            raise ValueError("OpenAI 호출 실패")

        response = {
                    "success" : "true",
                    "data" : [
                        {
                            "answer": answer
                        }
                    ]
                }

    except ValueError as e:
        response = {
                    "success" : "false",
                    "error_code" : 400,
                    "message" : "현재 AI 질문 요약이 어렵습니다. 잠시 후에 다시 사용해주세요."
                }
        response = json.dumps(response, ensure_ascii=False)

    except Exception as e:
        response = {
                    "success" : "false",
                    "error_code" : 500,
                    "message" : "현재 AI 질문 요약이 어렵습니다. 잠시 후에 다시 사용해주세요."
                }
        response = json.dumps(response, ensure_ascii=False)
        
    return jsonify(response)

if __name__ == '__main__':
    app.run(port="5000", host='0.0.0.0', debug=True)
