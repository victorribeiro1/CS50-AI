import sys
import copy

from crossword import *

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Initialize the crossword creator with a given crossword.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()  # Initialize domains for each variable with a copy of the words
            for var in self.crossword.variables
        }

    def letterGrid(self, assignment):
        """
        Create a 2D array (grid) representing the given assignment of letters.
        """
        letters = [
            [None for _ in range(self.crossword.width)]  # Create an empty grid of the crossword's width
            for _ in range(self.crossword.height)  # Create a grid for the crossword's height
        ]
        for variable, word in assignment.items():
            direction = variable.direction  # Get the direction of the variable
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)  # Row index based on direction
                j = variable.j + (k if direction == Variable.ACROSS else 0)  # Column index based on direction
                letters[i][j] = word[k]  # Assign the letter to the grid
        return letters

    def print(self, assignment):
        """
        Print the crossword assignment to the terminal.
        """
        letters = self.letterGrid(assignment)  # Get the grid representation
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:  # Check if the cell is part of the crossword
                    print(letters[i][j] or " ", end="")  # Print the letter or space if None
                else:
                    print("█", end="")  # Print a block for empty cells
            print()  # New line after each row

    def save(self, assignment, filename):
        """
        Save the crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cellSize = 100  # Size of each cell in the grid
        cellBorder = 2  # Border size for each cell
        interiorSize = cellSize - 2 * cellBorder  # Calculate interior size for text placement
        letters = self.letterGrid(assignment)  # Get the grid representation

        # Create a blank canvas for the image
        img = Image.new(
            "RGBA",
            (self.crossword.width * cellSize,
             self.crossword.height * cellSize),
            "black"  # Background color
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)  # Load the font
        draw = ImageDraw.Draw(img)  # Create a drawing context

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cellSize + cellBorder,
                     i * cellSize + cellBorder),
                    ((j + 1) * cellSize - cellBorder,
                     (i + 1) * cellSize - cellBorder)
                ]  # Define the rectangle for the cell
                if self.crossword.structure[i][j]:  # Check if the cell is part of the crossword
                    draw.rectangle(rect, fill="white")  # Draw the cell background
                    if letters[i][j]:  # If there is a letter
                        w, h = draw.textsize(letters[i][j], font=font)  # Get text size
                        draw.text(
                            (rect[0][0] + ((interiorSize - w) / 2),  # Center text horizontally
                             rect[0][1] + ((interiorSize - h) / 2) - 10),  # Center text vertically
                            letters[i][j], fill="black", font=font
                        )  # Draw the letter in the cell

        img.save(filename)  # Save the image to the specified filename

    def solve(self):
        """
        Solve the crossword by enforcing node and arc consistency.
        """
        self.enforceNodeConsistency()  # Ensure node consistency
        self.ac3()  # Enforce arc consistency
        return self.backtrack(dict())  # Start backtracking to find a solution

    def enforceNodeConsistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        """
        domainCopy = copy.deepcopy(self.domains)  # Create a deep copy of the domains

        # Iterate through the variables in the domain copy
        for variable in domainCopy:
            length = variable.length  # Get the length of the variable
            # Iterate through words in the copied domain
            for word in domainCopy[variable]:
                if len(word) != length:  # If word length does not match variable length
                    self.domains[variable].remove(word)  # Remove the word from the original domain

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        """
        xOverlap, yOverlap = self.crossword.overlaps[x, y]  # Get overlapping cells between x and y

        revisionMade = False  # Track if a revision was made

        domainsCopy = copy.deepcopy(self.domains)  # Make a deep copy of the domains

        if xOverlap:  # If there is an overlap
            # Iterate through words in x's domain
            for xWord in domainsCopy[x]:
                matchedValue = False  # Track if a matching value was found
                # Iterate through words in y's domain
                for yWord in self.domains[y]:
                    # Check if x's word and y's word have the same letter in the overlapping position
                    if xWord[xOverlap] == yWord[yOverlap]:
                        matchedValue = True
                        break  # No need to check the rest of y's words for this x
                if matchedValue:
                    continue  # Proceed to the next x if a match was found
                else:
                    self.domains[x].remove(xWord)  # Remove x's word as there was no matching y's word
                    revisionMade = True  # Mark that a revision was made

        return revisionMade  # Return if a revision was made

    def ac3(self, arcs=None):
        """
        Enforce arc consistency for the variables.
        """
        if not arcs:
            # Initialize queue with all arcs in the problem
            queue = []
            for variable1 in self.domains:
                for variable2 in self.crossword.neighbors(variable1):
                    if self.crossword.overlaps[variable1, variable2] is not None:
                        queue.append((variable1, variable2))  # Add the arc to the queue

        while len(queue) > 0:  # While there are arcs to process
            x, y = queue.pop(0)  # Get the next arc from the queue
            if self.revise(x, y):  # Revise the domain of x based on y
                if len(self.domains[x]) == 0:  # If x's domain is empty, return False
                    return False
                for neighbour in self.crossword.neighbors(x):
                    if neighbour != y:  # Add neighboring arcs to the queue
                        queue.append((neighbour, x))
        return True  # Return True if arc consistency is enforced without empty domains

    def assignmentComplete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.domains:  # Iterate through all variables in the domains
            if variable not in assignment:  # If any variable is not assigned a value
                return False  # Assignment is not complete
        return True  # All variables are assigned a value

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check if all values are distinct, every value is the correct length,
        # and there are no conflicts between neighboring variables.

        # Check if all values are distinct
        words = [*assignment.values()]  # Get all assigned words
        if len(words) != len(set(words)):  # If there are duplicate words
            return False  # Assignment is not consistent

        # Check if every value is the correct length
        for variable in assignment:
            if variable.length != len(assignment[variable]):  # If any word length is incorrect
                return False  # Assignment is not consistent

        # Check for conflicts between neighboring variables
        for variable in assignment:
            for neighbour in self.crossword.neighbors(variable):  # Iterate through neighbors of the variable
                if neighbour in assignment:  # If the neighbor is also assigned
                    x, y = self.crossword.overlaps[variable, neighbour]  # Get overlap indices
                    if assignment[variable][x] != assignment[neighbour][y]:  # If letters conflict
                        return False  # Assignment is not consistent

        # All checks passed, assignment is consistent
        return True

    def orderDomainValues(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Create a temporary dictionary to hold values and their eliminated counts
        wordDict = {}

        # Get neighbors of the variable
        neighbours = self.crossword.neighbors(var)

        # Iterate through words in the variable's domain
        for word in self.domains[var]:
            eliminated = 0  # Count of eliminated neighbor words
            for neighbour in neighbours:
                # Skip counting if the neighbor already has an assigned value
                if neighbour in assignment:
                    continue
                else:
                    # Calculate the overlap between the variable and its neighbor
                    xOverlap, yOverlap = self.crossword.overlaps[var, neighbour]
                    for neighbourWord in self.domains[neighbour]:  # Check each word in the neighbor's domain
                        # Count eliminated words based on the overlap
                        if word[xOverlap] != neighbourWord[yOverlap]:  # If letters do not match
                            eliminated += 1  # Increment eliminated count
            # Add the word and its eliminated count to the temporary dictionary
            wordDict[word] = eliminated

        # Sort the dictionary by the number of eliminated neighbor values
        sortedDict = {k: v for k, v in sorted(wordDict.items(), key=lambda item: item[1])}

        return [*sortedDict]  # Return the sorted list of words

    def selectUnassignedVariable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        choiceDict = {}  # Temporary dictionary for storing choices

        # Iterate through variables in the domains
        for variable in self.domains:
            # Check if the variable is not already assigned
            if variable not in assignment:
                choiceDict[variable] = self.domains[variable]  # Add to temporary dictionary

        # Create a list of variables sorted by the number of remaining values
        sortedList = [v for v, k in sorted(choiceDict.items(), key=lambda item: len(item[1]))]

        # Return the variable with the minimum number of remaining values
        return sortedList[0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # If assignment is complete
        if len(assignment) == len(self.domains):
            return assignment  # Return the complete assignment

        # Select one of the unassigned variables
        variable = self.selectUnassignedVariable(assignment)

        # Iterate through words in the variable's domain
        for value in self.domains[variable]:
            assignmentCopy = assignment.copy()  # Make a copy of the assignment
            assignmentCopy[variable] = value  # Assign the new value to the variable

            # Check for consistency with the new assignment
            if self.consistent(assignmentCopy):
                result = self.backtrack(assignmentCopy)  # Recursive backtrack call
                if result is not None:  # If a complete assignment is found
                    return result  # Return the complete assignment
        return None  # Return None if no assignment is possible

def main():
    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]  # Get crossword structure from command line
    words = sys.argv[2]  # Get words for the crossword from command line
    output = sys.argv[3] if len(sys.argv) == 4 else None  # Get optional output filename

    # Generate crossword
    crossword = Crossword(structure, words)  # Create a new Crossword object
    creator = CrosswordCreator(crossword)  # Create a new CrosswordCreator object
    assignment = creator.solve()  # Solve the crossword

    # Print result
    if assignment is None:
        print("No solution.")  # Print message if no solution found
    else:
        creator.print(assignment)  # Print the solved crossword
        if output:
            creator.save(assignment, output)  # Save the solved crossword if filename is provided

if __name__ == "__main__":
    main()  # Execute the main function if the script is run directly