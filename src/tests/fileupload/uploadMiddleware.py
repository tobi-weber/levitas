

from levitas.middleware.middleware import Middleware


class UploadMiddleware(Middleware):
    
    def post(self):
        #print(self.request_data)
        print("Upload finished")
        
        