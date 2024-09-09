import os
from dotenv import load_dotenv
from utils import query_refiner
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain.chains.conversation.memory import ConversationBufferWindowMemory

# .env 파일 로드
load_dotenv()

# OpenAI 및 Pinecone 초기화
pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index('wellda-prod')

# OpenAIEmbeddings 모델 초기화
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",  
    openai_api_key=os.getenv('OPENAI_API_KEY'), 
    dimensions=1024
)

class Document_:
    def __init__(self):
        # self.co = cohere.Client(os.environ['COHERE_API_KEY'])
        pass
    
    def context_to_string(self, contexts, query):
            context = '\n'.join(contexts)
            #print(context)
            if len(context) > 2000:
                context = context[:2000]
            if (len(context + query)) > 2500:
                context = context[:2500 - len(query)]
            return context

    def query_refine(self, query):
        return query_refiner(query)
    
    def find_match(self, query):
        # 쿼리 기반 문서 검색 및 매칭

        # dense vector로 변환
        dense_vec = embedding_model.embed_documents([query])
    
        # 하이브리드 써치 변경 시 가중치 사용 예정
        # sparse_vec = generate_sparse_vectors(input)
        # dense_vec, sparse_vec = hybrid_scale(
        #   dense_vec, sparse_vec, alpha=0.5
        # )

        # Pinecone 인덱스에서 쿼리 실행
        result = index.query(
            vector=dense_vec,
            # sparse_vector=sparse_vec,
            top_k=10, 
            include_values=True, 
            include_metadata=True
        )

        # 매칭된 결과를 점수 기준 내림차순 정렬
        result.matches.sort(key=lambda x: x.score, reverse=True)

        ref_list = []
        for res in result.matches:
            r = []
            # 유사도가 0.25 이상일 경우
            if res.score >= 0.25:
                # 매칭된 결과의 ID와 메타데이터 추출
                reference_id = res['id']

                # 키워드와 답변 부분 분리
                match_data = res['metadata']['guid']
                if "답변 :" in match_data:
                    keyword_part, answer_part = match_data.split("답변 :")
                    keywords = keyword_part.replace("키워드 :", "").strip().split("#")
                    keywords = [("#" + kw.strip()) for kw in keywords if kw]  # 키워드 전처리
                    answer = [answer_part.strip()]  # 답변 전처리
                else:
                    keywords = []
                    answer = []
                r = [reference_id, keywords, answer]

            else:
                # 유사도가 0.25 미만일 경우 빈 키워드와 답변 처리
                r = [reference_id, [], []]
            ref_list.append(r)

        return ref_list
