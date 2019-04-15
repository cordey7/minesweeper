from functools import reduce
from itertools import product
from operator import add
from random import sample
from tkinter import Button, Frame, Label, StringVar, Tk
from typing import Set, Tuple


def get_adjacent(index: Tuple[int, int]) -> Set[Tuple[int, int]]:
    """returns adjacent coordinates for input index"""

    x, y = index

    return {
        (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
        (x - 1, y),                 (x + 1, y),
        (x - 1, y + 1), (x, y + 1), (x + 1, y + 1),
        }


class Model(object):
    """creates a board and adds mines to it."""

    def __init__(self, width: int, height: int, num_mines: int):
        self.width = width
        self.height = height
        self.num_mines = num_mines        
        self.grid = self.create_grid()
        self.add_mines()        
        self.grid_coords = self.grid_coords()
        self.adjacent_mine_count()
        self.cells_revealed = set()     
        self.cells_flagged = set()
        self.revealed_zeroes = set()
        self.game_state = None

    def create_grid(self) -> list:

        return [[0] * self.width for _ in range(self.height)]

    def add_mines(self):
        """randomly adds mines to board"""

        for x, y in sample(list(product(range(self.width), range(self.height))), self.num_mines):
            self.grid[y][x] = 'm'

    def grid_coords(self) -> list:
        """returns a list of (x, y) coordinates for every position on grid"""

        return [(x, y) for y in range(self.height) for x in range(self.width)]

    def adjacent_mine_count(self):
        """counts the number of their surrounding mines"""

        def is_mine(coords):
            try:
                if coords[0] >= 0 and coords[1] >= 0:
                    return self.grid[coords[1]][coords[0]] == 'm'
                else:
                    return False
            except IndexError:
                return False

        for position in self.grid_coords: 
            x, y = position
            if self.grid[y][x] != "m":
                grid_value = reduce(add, map(is_mine, get_adjacent(position)))
                self.grid[y][x] = grid_value

    def get_cell_value(self, index: Tuple[int, int]) -> int or str:
        """cell value on click"""

        x, y = index
        return self.grid[y][x]

class View(Frame):
    """creates a GUI with a grid of cell buttons"""

    def __init__(self, width: int, height: int, 
                 num_mines: int, difficulty: str, controller: "Controller"):
        self.master = Tk()
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.difficulty = difficulty
        self.controller = controller
        self.color_dict = {
            0: 'white', 1: 'blue', 2: 'green',
            3: 'red', 4: 'orange', 5: 'purple',
            6: 'grey', 7: 'grey', 8: 'grey', "m": "black"
            }
        self.master.title('Minesweeper')

    def create_buttons(self) -> list:
        """create cell button widgets"""

        def create_button(x, y):
            button = Button(self.master, width=5, bg='yellow')
            button.grid(row=y + 5, column=x + 1)
            return button

        return [[create_button(x, y) for x in range(self.width)] 
                                     for y in range(self.height)]

    def initialize_bindings(self):
        """set up the reveal cell and the flag cell key bindings"""

        for x in range(self.width):
            for y in range(self.height):
                def closure_helper(f, index):
                    def g(_): 
                        f(index)                    
                    return g

                # Bind reveal decision method to left click
                self.buttons[y][x].bind(
                        '<Button-1>', closure_helper(
                        self.controller.reveal_decision, (x, y)))

                # Bind flag method to right click
                self.buttons[y][x].bind(
                        '<Button-3>', closure_helper(
                        self.controller.update_flagged_cell, (x, y)))

        # Set up reset button
        self.top_panel.reset_button.bind(
                '<Button>', lambda event: self.controller.reset(event))

    def reset_view(self):
        """destroys the GUI. Controller will create a new GUI"""

        self.master.destroy()

    def reveal_cell(self, index: Tuple[int, int], value: int or str):
        """reveals cell's value on GUI"""

        x, y = index
        self.buttons[y][x].configure(text=value, bg=self.color_dict[value])

    def flag_cell(self, index: Tuple[int, int]):
        """flag cell in GUI"""

        x, y = index
        self.buttons[y][x].configure(text="FLAG", bg="yellow")

    def unflag_cell(self, index: Tuple[int, int]):
        """unflag cell in GUI"""
        x, y = index
        self.buttons[y][x].configure(text="", bg="grey")

    def update_mines_left(self, mines: int):
        """updates mine counter widget"""

        self.top_panel.mine_count.set("Mines remaining: " + str(mines))

    def display_loss(self):
        """display the loss label when lose condition is reached"""

        self.top_panel.loss_label.grid(row=0, columnspan=10)

    def display_win(self):
        """display the win label when win condition is reached"""

        self.top_panel.win_label.grid(row=0, columnspan=10)

    def mainloop(self):
        self.top_panel = TopPanel(self.master, self.height, 
                                  self.width, self.num_mines)
        self.buttons = self.create_buttons()
        self.top_panel.mines_left.grid(row=0, columnspan=5)
        self.initialize_bindings()
        self.master.mainloop()


class TopPanel(Frame):
    """creates score board"""

    def __init__(self, master: Tk, width: int, height: int, num_mines: int):
        Frame.__init__(self, master)
        self.master = master
        self.num_mines = num_mines
        self.grid()

        self.reset_button = Button(self.master, width=7, text='Reset')
        self.reset_button.grid(row=0)

        self.loss_label = Label(text='You Lose!', bg='red')
        self.win_label = Label(text='You Win!', bg='green')

        self.mine_count = StringVar()
        self.mine_count.set('Mines: ' + str(self.num_mines))
        self.mines_left = Label(textvariable=self.mine_count)


class TextView(object):
    """creates a text interface of the minesweeper game"""

    def __init__(self, width: int, height: int, 
                 num_mines: int, difficulty: str, controller: "Controller"):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.controller = controller
        self.reveal_dict = {
            0: ' 0  ', 1: ' 1  ', 2: ' 2  ',
            3: ' 3  ', 4: ' 4  ', 5: ' 5  ',
            6: ' 6  ', 7: ' 7  ', 8: ' 8  ', "m": "mine"
            }
        self.cell_view = self.cell_view()
        self.show_grid()

    def cell_view(self)-> list:
        """create text view of cells"""

        return [["cell" for x in range(self.width)] 
                         for y in range(self.height)]

    def show_grid(self):
        """prints text grid to console. Includes column numbers"""

        top_row = [str(i) for i in range(self.width)]
        print(" ", *top_row, sep=" "*5)
        for row in range(len(self.cell_view)):
            print(str(row) + ":", *self.cell_view[row], sep="  ")

    def reveal_cell(self, index: Tuple[int, int], value: int or str):
        """Reveals a cell's value in the text view"""

        x, y = index
        self.cell_view[y][x] = self.reveal_dict[value]      

    def flag_cell(self, index: Tuple[int, int]):
        """Flags cell in cell_view"""

        x, y = index
        self.cell_view[y][x] = "FLAG"

    def unflag_cell(self, index: Tuple[int, int]):
        """Unflags cell in cell_view"""

        x, y = index
        self.cell_view[y][x] = "cell"

    def update_mines_left(self, mines):
        """Updates mine counter."""

        print("Mines remaining: " + str(mines))

    def display_loss(self):
        """Displays the lose label when loss condition is reached."""

        print("You Lose!")

    def display_win(self):
        """Displays the win label when win condition is reached."""

        print("You Win!")

    def mainloop(self):
        while True:
            try:
                cmd, *coords = input(
                        "Choose a cell in the format: "
                        + "flag/reveal x y. Type END to quit.  ").split()
                if cmd.lower()[0] == "e":
                    break
                x, y = coords[0], coords[1]
                if cmd.lower()[0] == "f":
                    self.controller.update_flagged_cell((int(x), int(y)))
                elif cmd.lower()[0] == "r":
                    self.controller.reveal_decision((int(x), int(y)))
                else:
                    print("Unknown command")
                self.show_grid()
            except:
                print("Incorrect selection or format")


class Controller(object):
    """Sets up button bindings and minesweeper game logic"""

    def __init__(self, width: int, height: int, 
                 num_mines: int, difficulty: str, view_type: str):
        self.width = width
        self.height = height
        self.num_mines = num_mines
        self.difficulty = difficulty       
        self.model = Model(self.width, self.height, self.num_mines)
        if view_type == "GUI":
            self.view = View(self.width, self.height, 
                             self.num_mines, self.difficulty, self)
        elif view_type == "TEXT":
            self.view = TextView(self.width, self.height, 
                                 self.num_mines, self.difficulty, self)
        self.view.mainloop()

    def reset(self, event):
        """Resets the game"""

        self.view.reset_view()        
        self.model = Model(self.width, self.height, self.num_mines)
        self.view = View(self.width, self.height, 
                         self.num_mines, self.difficulty, self)
        self.view.mainloop()

    def reveal_decision(self, index: Tuple[int, int]):
        """determine how to reveal cell."""

        x, y = index

        cell_value = self.model.get_cell_value(index)
        if index in self.model.cells_flagged:
            return None

        if cell_value in range(1, 9):
            self.reveal_cell(index, cell_value)

        elif (
                self.model.grid[y][x] == "m" 
                and self.model.game_state != "win"
                ):
            self.loss()

        else:
            self.reveal_zeroes(index)

#        Check for win condition
        cells_unrevealed = self.height * self.width - len(self.model.cells_revealed) 
        if cells_unrevealed == self.num_mines and self.model.game_state != "loss":
            self.win()

    def reveal_cell(self, index: Tuple[int, int], value: int or str):
        """obtains cell value from model and passes the value to view"""

        if index in self.model.cells_flagged:
            return None
        else:
            self.model.cells_revealed.add(index)
            self.view.reveal_cell(index, value)

    def reveal_adjacent(self, index: Tuple[int, int]):
        """counts the mines of 8 surrounding cells of clicked cell"""

        for coords in get_adjacent(index):
            if (
                    0 <= coords[0] <= self.width - 1 
                    and 0 <= coords[1] <= self.height - 1
                    ):
                cell_value = self.model.get_cell_value(coords)
                self.reveal_cell(coords, cell_value)

    def reveal_zeroes(self, index: Tuple[int, int]):
        """reveals all cells until a mine is reached"""

        val = self.model.get_cell_value(index)

        if val == 0:
            self.reveal_cell(index, val)
            self.reveal_adjacent(index)

            for coords in get_adjacent(index):
                if (
                        0 <= coords[0] <= self.width - 1
                        and 0 <= coords[1] <= self.height - 1
                        and self.model.get_cell_value(coords) == 0
                        and coords not in self.model.revealed_zeroes
                        ):
                    self.model.revealed_zeroes.add(coords)
                    self.reveal_zeroes(coords)

    def update_flagged_cell(self, index: Tuple[int, int]):
        """Flag/unflag cells for possible mines. Does not reveal cell."""

        if (
                index not in self.model.cells_revealed 
                and index not in self.model.cells_flagged
                ):
            self.model.cells_flagged.add(index)
            self.view.flag_cell(index)

        elif (
                index not in self.model.cells_revealed 
                and index in self.model.cells_flagged
                ):
            self.model.cells_flagged.remove(index)
            self.view.unflag_cell(index)

        self.update_mines()

    def update_mines(self):
        """update mine counter"""

        mines_left = self.num_mines - len(self.model.cells_flagged)

        if mines_left >= 0:
            self.view.update_mines_left(mines_left)

    def win(self):
        """winner"""

        self.model.game_state = "win"
        self.view.display_win()

    def loss(self):
        """you lost show all cells."""

        self.model.game_state = "loss"
        self.view.display_loss()

#        Reveals all cells
        for row in range(self.height):
            for col in range(self.width):
                cell_value = self.model.get_cell_value((col,row))
                self.view.reveal_cell((col, row), cell_value)


class InitializeGame(Frame):
    """starts game. Allows player to choose difficulty"""

    def __init__(self):
        self.root = Tk()        
        self.create_view_choice()
        self.create_difficulty_widgets()
        self.root.mainloop()

    def create_view_choice(self):
        "creates widgets allowing player to choose a view type."""

        self.view_label = Label(self.root, text="Choose game type")
        self.view_label.grid()
        self.view_types = ["GUI", "TEXT"]
        def create_button(view_type):
            button = Button(self.root, width=7, bg='grey', text=view_type)
            button.grid()
            return button

        self.view_widgets = [
                create_button(view_type) for view_type in self.view_types
                ] + [self.view_label]

        for i in range(2):
            def closure_helper(f, view_choice):
                    def g(_): 
                        f(view_choice)                    
                    return g
            self.view_widgets[i].bind("<Button>", closure_helper(
                    self.set_up_difficulty_widgets, self.view_types[i]))

    def create_difficulty_widgets(self):
        """create buttons for difficulty."""

        self.diff_label = Label(self.root, text="Choose difficulty")
        self.difficulty = ("Easy", "Medium", "Hard")
        def create_button(difficulty):
            button = Button(self.root, width=7, bg='red', text=difficulty)
            return button

        self.difficulty_widgets = [create_button(diff) 
                                    for diff in self.difficulty]
        self.difficulty_widgets = [self.diff_label] + self.difficulty_widgets

    def set_up_difficulty_widgets(self, view_type: str):
        """removes view buttons. Sets up difficulty options for view chosen"""

        for widget in self.view_widgets:
            widget.grid_remove()

        if view_type == "TEXT":
            self.difficulty_widgets[0].grid()
            self.difficulty_widgets[1].grid()
        else:
            for widget in self.difficulty_widgets:
                widget.grid()
        self.bind_difficulty_widgets(view_type)

    def bind_difficulty_widgets(self, view_type: str):
        """binds difficulty buttons"""

        for i in range(1, 4):
            def closure_helper(f, difficulty, view_type):
                    def g(_): 
                        f(difficulty, view_type)                    
                    return g
            self.difficulty_widgets[i].bind(
                    "<Button>", closure_helper(
                    self.init_game, self.difficulty[i - 1], view_type))

    def init_game(self, difficulty: str, view_type: str):
        """starts game"""

        self.root.destroy()
        return Controller(*{
                            'E': (10, 10, 10, difficulty, view_type),
                            'M': (16, 16, 40, difficulty, view_type),
                            'H': (25, 20, 99, difficulty, view_type)
                            }[difficulty[0]])


if __name__ == "__main__":
    game = InitializeGame() 