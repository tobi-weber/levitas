
from levitas.middleware.fileMiddleware import FileMiddleware

from .uploadMiddleware import UploadMiddleware


httpserver_address = ("127.0.0.1", 9090)


upload_path = "/home/tobi/temp/UPLOAD"

                         
urls = [
(r"^/upload$", UploadMiddleware),
(r"^/(upload.html|upload5.html|js/(.*)|css/(.*))$", FileMiddleware, {"path":
            "/home/tobi/Workspaces/Public/levitas/src/tests/fileupload"}),
]
