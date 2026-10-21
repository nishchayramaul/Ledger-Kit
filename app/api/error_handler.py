from xml.dom.pulldom import ErrorHandler

from app.core.error import AppError


class ErrorHandler(ErrorHandler):
    def __init__(self, error: AppError):
        self.error = error