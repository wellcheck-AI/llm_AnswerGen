from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(app, version='1.0', title='My API',
          description='A simple API with Swagger documentation',
          doc='/docs'  # Swagger UI 경로
         )

ns = api.namespace('summary', description='Summary operations')

# 모델 정의 (Swagger 문서에 표시됨)
summary_model = api.model('Summary', {
    'query': fields.String(required=True, description='The query to be summarized')
})

@ns.route('/')
class Summary(Resource):
    @api.expect(summary_model)
    @api.response(200, 'Success')
    @api.response(400, 'Validation Error')
    def post(self):
        """
        Summarize a given query.
        """
        data = request.json
        query = data.get('query', '')
        return jsonify({"summary": f"Summary of {query}"})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
