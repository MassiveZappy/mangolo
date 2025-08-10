# enums to define: Mongolo Datatypes
from enum import Enum

class MongoloDataType(Enum):
    FILE = 1
    DIRECTORY = 2
    INT = 3
    FLOAT = 4
    DECIMAL = 5
    STRING = 6
    BOOLEAN = 7
    LIST = 8
    DICT = 9

class TreeTokenKinds(Enum):
    NEWCOMMAND = 1
    FILE = 2
    DBTYPE = 3

class fileReader:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = None

    def checkExistence(self, makeFile=False):
        import os
        if not os.path.exists(self.file_path):
            if makeFile:
                os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
                with open(self.file_path, 'w') as file:
                    pass
            else:
                raise FileNotFoundError(f"The file {self.file_path} does not exist.")

    def load(self):
        with open(self.file_path, 'r') as file:
            return self.loads(file.read())

    def loads(self, data):
        raise NotImplementedError("Subclasses should implement this method.")

    def dump(self, data):
        with open(self.file_path, 'w') as file:
            file.write(self.dumps(data))

    def dumps(self, data):
        raise NotImplementedError("Subclasses should implement this method.")

class Token:
    def __init__(self, kind, value, line=None, column=None):
        self.kind = kind
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.kind}, {self.value}, line={self.line}, column={self.column})"

class lexer:
    def __init__(self, data):
        self.data = data
        self.position = 0
        self.char = None
        self.line = 1
        self.column = 1

    def advance(self):
        if self.position < len(self.data):
            self.char = self.data[self.position]
            self.position += 1
            if self.char == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            return self.char
        return None

    def peek(self, offset = 1):
        if self.position + offset - 1 < len(self.data):
            return self.data[self.position + offset - 1]
        return None

    def tokenize(self):
        raise NotImplementedError("Subclasses should implement this method.")

class treeLexer(lexer):
    def __init__(self, data):
        super().__init__(data)
        self.tokens = []

    def tokenize(self):
        pass

class treeParser:
