#!d/usr/bin/python3 -u
import json
from dotenv import load_dotenv
from flask_cors import CORS
from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields

from document import Document_
from chat import Chatbot_

# .env 파일 로드
load_dotenv()

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSON_AS_ASCII'] = False
CORS(app) 

api = Api(app, version='1.0', title='API Document',
          description='Coach assistant Chatbot API Document',
          doc='/docs/'
         )

ns_summary = api.namespace('summary', description='요약 API')
ns_reference = api.namespace('reference', description='참고 문서 검색 API')
ns_answer = api.namespace('answer', description='답변 생성 API')

summary_model = api.model('Summary', {
    'query': fields.String(required=True, description='요약할 사용자의 질문 입력')
})

reference_model = api.model('Reference', {
    'query': fields.String(required=True, description='답변을 생성하기 위해 필요한 문서를 검색하기 위해 질문 입력')
})

answer_model = api.model('Answer', {
    'query': fields.String(required=True, description='답변을 생성할 사용자의 질문 입력'),
    'data': fields.List(fields.Raw(), required=True, description='검색된 문서의 인덱스와 내용을 리스트 형태로 입력')
})

llm = Chatbot_()
document = Document_()

@ns_summary.route('/')
class Summary(Resource):
    @api.expect(summary_model)
    @api.response(200, 'Success')
    @api.response(400, 'ValueError')
    @api.response(500, 'Error')
    def post(self):
        try:
            data = request.json
            query = data['query']

            try:
                summary = llm.summary(query)
            except:
                raise ValueError("OpenAI 호출 실패")

            response = {
                "success": "true",
                "data": [
                    {
                        "summary": summary,
                    }
                ]
            }

        except ValueError as e:
            response = {
                "success": "false",
                "error_code": 400,
                "message": "현재 AI 질문 요약이 어렵습니다. 잠시 후에 다시 사용해주세요."
            }

        except Exception as e:
            response = {
                "success": "false",
                "error_code": 500,
                "message": "현재 AI 질문 요약이 어렵습니다. 잠시 후에 다시 사용해주세요."
            }

        return jsonify(response)

@ns_reference.route('/')
class Reference(Resource):
    @api.expect(reference_model)
    @api.response(200, 'Success')
    @api.response(400, 'ValueError')
    @api.response(500, 'Error')
    def post(self):
        try:
            data = request.json
            query = data['query']

            try:
                query_refine = document.query_refine(query)
                context = document.find_match(query_refine)

            except:
                raise ValueError("OpenAI 호출 실패")

            reference = {"reference": []} 

            for i, c in enumerate(context, start=1):
                reference["reference"].append({
                    "index": c[0],
                    "keyword": c[1],
                    "text": c[2][0],
                })

            response = {
                "success": "true",
                "data": [
                    reference
                ]
            }

        except ValueError as e:
            response = {
                "success": "false",
                "error_code": 400,
                "message": "현재 AI 질문 요약이 어렵습니다. 잠시 후에 다시 사용해주세요."
            }
            response = json.dumps(response, ensure_ascii=False)

        except Exception as e:
            response = {
                "success": "false",
                "error_code": 500,
                "message": "현재 AI 질문 요약이 어렵습니다. 잠시 후에 다시 사용해주세요."
            }
            response = json.dumps(response, ensure_ascii=False)

        return jsonify(response)

# Answer 리소스 클래스 정의
@ns_answer.route('/')
class Answer(Resource):
    @api.expect(answer_model)
    @api.response(200, 'Success')
    @api.response(400, 'ValueError')
    @api.response(500, 'Error')
    def post(self):
        try:
            json_data = request.json
            query = json_data['query']
            # index_list = json_data['data'][0]['index']
            reference_list = json_data['data'][0]['reference']

            context = document.context_to_string(reference_list, query)

            try:
                if context:
                    reference=context
                else:
                    reference=['참고문서는 없으니 확실한 정보 기반으로 대답해줘.']
                answer = "(자동화 답변)" + llm.getConversation_prompttemplate(query=query, reference=reference)
                
            except:
                raise ValueError("OpenAI 호출 실패")

            response = {
                "success": "true",
                "data": [
                    {
                        "answer": answer
                    }
                ]
            }
            print(response)

        except ValueError as e:
            response = {
                "success": "false",
                "error_code": 400,
                "message": "현재 AI 질문 요약이 어렵습니다. 잠시 후에 다시 사용해주세요."
            }
            response = json.dumps(response, ensure_ascii=False)

        except Exception as e:
            response = {
                "success": "false",
                "error_code": 500,
                "message": "현재 AI 질문 요약이 어렵습니다. 잠시 후에 다시 사용해주세요."
            }
            response = json.dumps(response, ensure_ascii=False)

        return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
