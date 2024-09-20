class PineconeAPIKeyError(Exception):
    def __init__(self, error_log):
        super().__init__(f"{str(error_log)}\nPineconeAPIKeyError: Invalid Pinecone API Key")
    
class PineconeIndexNameError(Exception):
    def __str__(self):
        return "index does not exists"
    
class PineconeUnexceptedException(Exception):
    def __init__(self, error_log):
        super().__init__(f"{str(error_log)}\nPineconeUnexceptedException")