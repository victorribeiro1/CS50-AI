class Variable():
    # Constants for directions
    ACROSS = "across"
    DOWN = "down"

    def __init__(self, i, j, direction, length):
        """Create a new variable with starting point, direction, and length."""
        self.i = i  # Row index where the variable starts
        self.j = j  # Column index where the variable starts
        self.direction = direction  # Direction of the variable (ACROSS or DOWN)
        self.length = length  # Length of the variable
        self.cells = []  # List to store the cells occupied by the variable

        # Generate the list of cells occupied by this variable
        for k in range(self.length):
            self.cells.append(
                (self.i + (k if self.direction == Variable.DOWN else 0),  # Adjust row index for DOWN direction
                 self.j + (k if self.direction == Variable.ACROSS else 0))  # Adjust column index for ACROSS direction
            )

    def __hash__(self):
        """Return a hash value for the variable."""
        return hash((self.i, self.j, self.direction, self.length))

    def __eq__(self, other):
        """Check equality between this variable and another."""
        return (
            (self.i == other.i) and
            (self.j == other.j) and
            (self.direction == other.direction) and
            (self.length == other.length)
        )

    def __str__(self):
        """Return a string representation of the variable."""
        return f"({self.i}, {self.j}) {self.direction} : {self.length}"

    def __repr__(self):
        """Return a detailed string representation of the variable for debugging."""
        direction = repr(self.direction)
        return f"Variable({self.i}, {self.j}, {direction}, {self.length})"


class Crossword():
    def __init__(self, structureFile, wordsFile):
        """Initialize the crossword structure and the word list."""
        # Determine the structure of the crossword from a file
        with open(structureFile) as f:
            contents = f.read().splitlines()
            self.height = len(contents)  # Height of the crossword grid
            self.width = max(len(line) for line in contents)  # Width of the crossword grid

            self.structure = []  # 2D list representing the crossword structure
            for i in range(self.height):
                row = []
                for j in range(self.width):
                    # Fill the structure with True (empty space) or False (blocked space)
                    if j >= len(contents[i]):
                        row.append(False)
                    elif contents[i][j] == "_":
                        row.append(True)
                    else:
                        row.append(False)
                self.structure.append(row)

        # Save vocabulary list from the words file
        with open(wordsFile) as f:
            self.words = set(f.read().upper().splitlines())  # Convert words to uppercase and store in a set

        # Determine the set of variables (words that can be placed in the crossword)
        self.variables = set()
        for i in range(self.height):
            for j in range(self.width):
                # Identify vertical words
                startsWord = (
                    self.structure[i][j]  # Check if the cell is empty
                    and (i == 0 or not self.structure[i - 1][j])  # Check if it's the start of a vertical word
                )
                if startsWord:
                    length = 1
                    # Calculate the length of the vertical word
                    for k in range(i + 1, self.height):
                        if self.structure[k][j]:  # Continue while there are empty spaces
                            length += 1
                        else:
                            break
                    if length > 1:  # Only add words with length greater than 1
                        self.variables.add(Variable(
                            i=i, j=j,
                            direction=Variable.DOWN,
                            length=length
                        ))

                # Identify horizontal words
                startsWord = (
                    self.structure[i][j]  # Check if the cell is empty
                    and (j == 0 or not self.structure[i][j - 1])  # Check if it's the start of a horizontal word
                )
                if startsWord:
                    length = 1
                    # Calculate the length of the horizontal word
                    for k in range(j + 1, self.width):
                        if self.structure[i][k]:  # Continue while there are empty spaces
                            length += 1
                        else:
                            break
                    if length > 1:  # Only add words with length greater than 1
                        self.variables.add(Variable(
                            i=i, j=j,
                            direction=Variable.ACROSS,
                            length=length
                        ))

        # Compute overlaps for each word
        # For any pair of variables v1, v2, their overlap is either:
        #    None, if the two variables do not overlap; or
        #    (i, j), where v1's ith character overlaps v2's jth character
        self.overlaps = dict()  # Dictionary to store overlaps between variables
        for v1 in self.variables:
            for v2 in self.variables:
                if v1 == v2:  # Skip if both variables are the same
                    continue
                cells1 = v1.cells
                cells2 = v2.cells
                intersection = set(cells1).intersection(cells2)  # Find overlapping cells
                if not intersection:  # No overlap
                    self.overlaps[v1, v2] = None
                else:
                    intersection = intersection.pop()  # Get one overlapping cell
                    self.overlaps[v1, v2] = (
                        cells1.index(intersection),  # Index of the overlap in v1
                        cells2.index(intersection)   # Index of the overlap in v2
                    )

    def neighbors(self, var):
        """Given a variable, return the set of overlapping variables."""
        return set(
            v for v in self.variables
            if v != var and self.overlaps[v, var]  # Exclude the variable itself and check for overlaps
        )
