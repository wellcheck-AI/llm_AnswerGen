import os
from dotenv import load_dotenv
from utils import query_refiner
from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain.chains.conversation.memory import ConversationBufferWindowMemory

load_dotenv()

pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index('wellda-test')

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",  
    openai_api_key=os.getenv('OPENAI_API_KEY'), 
    dimensions=1024
)

class Document_:
    def __init__(self):
        pass
    
    def context_to_string(self, contexts, query):
            context = '\n'.join(contexts)
            if len(context) > 2000:
                context = context[:2000]
            if (len(context + query)) > 2500:
                context = context[:2500 - len(query)]
            return context

    def query_refine(self, query):
        return query_refiner(query)
    
    def find_match(self, query):

        dense_vec = embedding_model.embed_documents([query])
    
        result = index.query(
            vector=dense_vec,
            top_k=10, 
            include_values=True, 
            include_metadata=True
        )

        result.matches.sort(key=lambda x: x.score, reverse=True)

        ref_list = []
        for res in result.matches:
            r = []
            if res.score >= 0.25:
                reference_id = res['id']

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
                reference_id = None
                r = [reference_id, [], []]
                ref_list.append(r)

        return ref_list
    