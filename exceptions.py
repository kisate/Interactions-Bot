class NoToolException(BaseException):
    def __init__(self, tool):
        BaseException.__init__(self)
        self.tool = tool

class ChunkNotLoadedException(BaseException):
    def __init__(self, chunk_coords):
        BaseException.__init__(self)
        self.chunk_coords = chunk_coords

class TooManyArgumentsException(BaseException):
    def __init__(self, arguments):
        BaseException.__init__(self)
        self.arguments = arguments