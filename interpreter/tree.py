import json
import utils

class tree:
    """
    Simmilar to the json class, but loads tree files.
    Tree file example:
    /path/to/databaseOutline.mango databaseType
    """
    def __init__(self):
        super().__init__()

    def loads(self, file):
        """
        Loads a tree from a file.
        The file should contain a JSON-like structure representing the tree.
        """
        with open(file, 'r') as f:
            data = json.load(f)
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
