import pinecone
from pinecone import Pinecone
import pinecone.core
import pinecone.core.openapi.shared
import pinecone.core.openapi.shared.exceptions

from exceptions import PineconeIndexNameError, PineconeUnexceptedException
import pinecone.core.openapi

class PineconeCursor:
    def __init__(self, api_key:str, index_name:str):
        self.pinecone_api_key = api_key
        self.index_name = index_name
    
    def query(self, **kwargs):
        try:
            pc = Pinecone(api_key=self.pinecone_api_key)
            existing_indexes = [index.name for index in pc.list_indexes()]

            if self.index_name not in existing_indexes:
                raise PineconeIndexNameError
            
            self.index = pc.Index(self.index_name)
        
        except pinecone.exceptions.PineconeApiException as e:
            raise pinecone.exceptions.PineconeApiException(e)
        
        except PineconeIndexNameError as e:
            raise PineconeIndexNameError
        
        except Exception as e:
            raise PineconeUnexceptedException(e)

        return self.index.query(**kwargs)