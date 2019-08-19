class NoToolException(BaseException):
    def __init__(self, tool):
        BaseException.__init__(self)
        self.tool = tool