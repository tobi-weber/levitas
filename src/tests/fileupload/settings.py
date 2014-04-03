
from levitas.middleware.fileMiddleware import FileMiddleware
from levitas.lib.levitasFieldStorage import LevitasFieldStorage

from .uploadMiddleware import UploadMiddleware


httpserver_address = ("127.0.0.1", 9090)

fieldstorage_class = LevitasFieldStorage
upload_path = "/home/tobi/temp/UPLOAD"

                         
urls = [
(r"^/upload$", UploadMiddleware),
(r"^/(upload.html|upload5.html|js/(.*)|css/(.*))$", FileMiddleware, {"path":
            "/home/tobi/Workspaces/Public/levitas/src/tests/fileupload"}),
]
