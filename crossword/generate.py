import sys

from crossword import *

class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            words2remove = set()

            for word in self.domains[variable]:
                if len(word) != variable.length:
                    words2remove.add(word)

            for x in words2remove:
                self.domains[variable].remove(x)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.
        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False

        if self.crossword.overlaps[x, y] is not None:
            words2remove = set()
            
            for wordX in self.domains[x]:
                charY = []
                overlapping_char = wordX[self.crossword.overlaps[x, y][0]]
                for wordY in self.domains[y]:
                    charY.append(wordY[self.crossword.overlaps[x, y][1]])
                if overlapping_char not in charY:
                    words2remove.add(wordX)
                    revise = True

            for word in words2remove:
                self.domains[x].remove(word)

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.
        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if arcs is None:
            queue = []
            for v1 in self.crossword.variables:
                for v2 in self.crossword.variables:
                    if v1 != v2 and self.crossword.overlaps[v1, v2] is not None:
                        queue.append((v1, v2))
        else:
            queue = arcs

        while queue:
            arc = queue.pop(0)
            x, y = arc[0], arc[1]

            if self.revise(x, y):
                if not self.domains[x]:
                    return False

                for neighbor in self.crossword.neighbors(x):
                    if neighbor != y:
                        queue.append((neighbor, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        return set(assignment.keys()) == self.crossword.variables and all(assignment.values())
        
    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        if len(set(assignment.values())) != len(set(assignment.keys())):
            return False

        for v in assignment:
            if len(assignment[v]) != v.length:
                return False
            
            for neighbor in self.crossword.neighbors(v):
                if neighbor in assignment:
                    overlap = self.crossword.overlaps[v, neighbor]
                    if assignment[v][overlap[0]] != assignment[neighbor][overlap[1]]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        num_eliminated = {}
        for word in self.domains[var]:
            num_eliminated[word] = 0
        
        for wordV in self.domains[var]:
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment.keys():
                    i, j = self.crossword.overlaps[var, neighbor]

                    for wordN in self.domains[neighbor]:
                        if wordV[i] != wordN[j]:
                            num_eliminated[wordV] += 1

        sorted_list = []
        for i in sorted(num_eliminated.items(), key=lambda n:n[1]):
            sorted_list.append(i[0])
        return sorted_list


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
##        print(unassigned_variables)
        unassigned_variables = set()
        for v in self.crossword.variables:
            if v not in assignment.keys():
                unassigned_variables.add(v)
                
        num_remaining_values = {}
        for v in unassigned_variables:
            num_remaining_values[v] = len(self.domains[v])
        num_remaining_values = sorted(num_remaining_values.items(), key=lambda n:n[1])

        if len(num_remaining_values) == 1 or num_remaining_values[0][1] != num_remaining_values[1][1]:
            return num_remaining_values[0][0]
        else:
            num_degrees = {}
            for v in unassigned_variables:
                num_degrees[v] = len(self.crossword.neighbors(v))
            num_degrees = sorted(num_degrees.items(), key=lambda n:n[1], reverse=True)
            return num_degrees[0][0]

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.
        `assignment` is a mapping from variables (keys) to words (values).
        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result
        return None        

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
