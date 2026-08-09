class BusinessException(Exception):
    """业务通用异常"""
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        