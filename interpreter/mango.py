import utils
from enum import Enum
from interpreter.mongoloFiles import language

class mango:
    """
    Definition for a database.
    Slice files in the same directory as the mango file represent the table objects.
    Knive files in the same directory represent the data hygene check programming language.
    """
    def __init__(self):
        super().__init__()


    def loads(self, file):
        """
        Loads a mango information a file.
        The file should contain a JSON-like structure representing the tree.
        """
        with open(file, 'r') as f:
            data = f.read()
        return self.load(data)



    def load(self, data):
        """
        Loads a tree from a JSON-like structure.
        The structure should be a dictionary with the following keys
        """
        lines = []
        for line in data.splitlines():
            commentStart = line.find("#")
            if commentStart != -1:
                line = line[:commentStart]
            line = line.strip()
            if line:
                lines.append(line)
        if not lines:
            raise utils.lexerError("Empty tree file", 0, 0)

        output = []

        for line in lines:
            parts = line.split()
            if len(parts) < 2:
                raise utils.lexerError(f"Invalid tree line: {line}", 0, 0)
            path = parts[0]
            dbType = parts[1]
            output.append((path, dbType))

        return output
    # Dump is not supported, as mango files are meant to be written manualy.
