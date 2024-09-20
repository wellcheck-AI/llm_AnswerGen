import pinecone
from pinecone import Pinecone
import pinecone.core
import pinecone.core.openapi.shared
import pinecone.core.openapi.shared.exceptions

from exceptions import PineconeAPIKeyError, PineconeIndexNameError, PineconeUnexceptedException
import pinecone.core.openapi

class PineconeCursor:
    def __init__(self, api_key:str, index_name:str):
        self.pinecone_api_key = api_key
        self.index_name = index_name
    
    def query(self, **kwargs):
        try:
            pc = Pinecone(api_key=self.pinecone_api_key)
        except Exception as e:
            raise PineconeUnexceptedException(e) from None

        try:
            existing_indexes = [index.name for index in pc.list_indexes()]
        except pinecone.core.openapi.shared.exceptions.UnauthorizedException as e:
            raise PineconeAPIKeyError(e) from None

        if self.index_name not in existing_indexes:
            raise PineconeIndexNameError
        
        try:
            self.index = pc.Index(self.index_name)
        except Exception as e:
            raise PineconeUnexceptedException(e) from None
        
        return self.index.query(**kwargs)