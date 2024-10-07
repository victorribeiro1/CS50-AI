import itertools
import random
import copy
from typing import TYPE_CHECKING


class Minesweeper():
    """
    Representation of the Minesweeper game.
    """

    def __init__(self, height=8, width=8, mines=8):

        # Initialize height, width, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Create an empty board with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Randomly place mines on the board
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # Initially, the player has not found any mines
        self.mines_found = set()

    def print(self):
        """
        Displays a text representation of the mine locations.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Counts the number of mines adjacent to a given cell,
        excluding the cell itself.
        """

        # Count nearby mines
        count = 0

        # Iterate over all adjacent cells
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Skip the cell itself
                if (i, j) == cell:
                    continue

                # Increase count if the cell is within bounds and contains a mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Verifies if all mines have been successfully flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    A logical statement about a Minesweeper game.
    A sentence consists of a set of board cells
    and a count of the number of those cells that are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the cells in self.cells that are confirmed as mines.
        """
        if len(self.cells) == self.count:
            return copy.deepcopy(self.cells)
        
        return None

    def known_safes(self):
        """
        Returns the cells in self.cells that are confirmed as safe.
        """
        if self.count == 0:
            return copy.deepcopy(self.cells)

        return None

    def mark_mine(self, cell):
        """
        Updates the internal representation based on the knowledge
        that a cell is confirmed as a mine.
        """
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1   

    def mark_safe(self, cell):
        """
        Updates the internal representation based on the knowledge
        that a cell is confirmed as safe.
        """
        if cell in self.cells:
            self.cells.discard(cell)


class MinesweeperAI():
    """
    Represents the player in the Minesweeper game.
    """

    def __init__(self, height=8, width=8):

        # Initialize height and width
        self.height = height
        self.width = width

        # Track which cells have been selected
        self.moves_made = set()

        # Track known safe cells and mines
        self.mines = set()
        self.safes = set()

        # List of sentences that represent the game's knowledge
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Identifies a cell as a mine and updates all knowledge
        to reflect that it is a mine.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Identifies a cell as safe and updates all knowledge
        to reflect that it is safe.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Invoked when the Minesweeper board indicates how many neighboring
        cells contain mines for a given safe cell.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base based on
               the provided `cell` and `count`
            4) mark any additional cells as safe or mines based on
               conclusions from the AI's knowledge base
            5) append new sentences to the AI's knowledge base if
               they can be inferred from existing knowledge
        """

        # 1 & 2
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # 3
        surrounding_cells = self.get_surrounding_cells(cell)
        sentence = Sentence(surrounding_cells, count)
        self.knowledge.append(sentence)
        
        # 4
        for s in self.knowledge:
            known_mines = s.known_mines()
            known_safes = s.known_safes()

            if known_mines:
                for mineCell in known_mines:
                    self.mark_mine(mineCell)
            
            if known_safes:
                for safeCell in known_safes:
                    self.mark_safe(safeCell)

        # 5
        for i, s1 in enumerate(self.knowledge):
            for j, s2 in enumerate(self.knowledge):
                if s1.cells in s2.cells and i != j:
                    newSentence = Sentence(set(s2.cells - s1.cells), s2.count - s1.count)
                    self.knowledge.append(newSentence)
        

    def make_safe_move(self):
        """
        Selects a safe cell to move to on the Minesweeper board.
        The move must be confirmed safe and not already made.
        This function may use the knowledge in self.mines, self.safes,
        and self.moves_made, but should not alter any of those values.
        """
        
        if self.safes:
            for safe in self.safes:
                if safe not in self.moves_made:
                    return copy.deepcopy(safe)
        
        return None

    def make_random_move(self):
        """
        Chooses a move on the Minesweeper board at random.
        The move must be among cells that:
            1) have not been previously selected, and
            2) are not confirmed as mines
        """

        if not self.moves_made:
            return (random.randint(0, self.height - 1), random.randint(0, self.width - 1))

        allCells = self.get_all_cells()
        uncertainCells = (allCells - self.moves_made) - self.mines

        try:
            return uncertainCells.pop()
        except Exception:
            print("NO UNCERTAIN CELLS")
            return None

    def get_all_cells(self):
        allCells = set()
        for i in range(0, self.height):
            for j in range(0, self.width):
                allCells.add((i, j))
        return allCells

    def get_surrounding_cells(self, cell):
        surrounding_cells = set()

        for i in range(0, 3):
            for j in range(0, 3):
                y = i + cell[0] - 1
                x = j + cell[1] - 1
                if x >= 0 and x < self.width and y >= 0 and y < self.height and (y, x) != cell and (y, x) not in self.moves_made:
                    surrounding_cells.add((y, x))
                
        return surrounding_cells