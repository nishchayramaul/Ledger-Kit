



class AppError(Exception):
    status: int = 500
    type_slug:str = "internal_server_error"
    title: str = "Internal Server Error"


    def __init__(self, detail: str):
        super().__init__(detail)
        self.detail = detail


