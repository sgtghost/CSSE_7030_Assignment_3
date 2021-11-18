"""
CSSE1001 Assignment 3
Semester 2, 2020
"""

# Fill these in with your details
__author__ = "{{Tie Wang}} ({{s4621539}})"
__email__ = "tie.wang@uqconnect.edu.au"
__date__ = "2020/10/20"

# Write your code here

"""Import the needed libraries """
import tkinter as tk
from tkinter import messagebox
from tkinter.filedialog import askopenfilename, asksaveasfile
from PIL import Image, ImageTk


"""TASK CONSTANTS"""
TASK_ONE = 1
TASK_TWO = 2
MASTERS = 3

"""This is the start of content from a2_support.py"""

GAME_LEVELS = {
    # dungeon layout: max moves allowed
    "game1.txt": 7,
    "game2.txt": 12,
    "game3.txt": 19,
}

PLAYER = "O"
KEY = "K"
DOOR = "D"
WALL = "#"
MOVE_INCREASE = "M"
SPACE = " "

DIRECTIONS = {
    "w": (-1, 0),
    "s": (1, 0),
    "d": (0, 1),
    "a": (0, -1)
}

INVESTIGATE = "I"
QUIT = "Q"
HELP = "H"

VALID_ACTIONS = [INVESTIGATE, QUIT, HELP, *DIRECTIONS.keys()]

HELP_MESSAGE = f"Here is a list of valid actions: {VALID_ACTIONS}"

INVALID = "That's invalid."

WIN_TEXT = "You have won the game with your strength and honour!"

LOSE_TEST = "You have lost all your strength and honour."
LOSE_TEXT = "You have lost all your strength and honour."


def load_game(filename):
    """Create a 2D array of string representing the dungeon to display.
    
    Parameters:
        filename (str): A string representing the name of the level.

    Returns:
        (list<list<str>>): A 2D array of strings representing the 
            dungeon.
    """
    dungeon_layout = []

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            dungeon_layout.append(list(line))

    return dungeon_layout

"""This is the end of content from a2_support.py"""

"""This is the start of model classes."""
class Entity:
    """A generic Entity within the game."""

    _id = "Entity"

    def __init__(self):
        """
        Something the player can interact with
        """
        self._collidable = True

    def get_id(self):
        """(str)Returns a string that represents the Entity’s ID"""
        return self._id

    def set_collide(self, collidable):
        """Set the collision state for the Entity.

        Parameters:
            collidable(bool): The collision state.
        """
        self._collidable = collidable

    def can_collide(self):
        """(bool)Return the collision state for the Entity."""
        return self._collidable

    def __str__(self):
        return f"{self.__class__.__name__}({self._id!r})"

    def __repr__(self):
        return str(self)


class Wall(Entity):
    """A special type of Entity within the game."""

    _id = WALL
    
    def __init__(self):
        """Wall should be constructed with Wall(),no addtional argument required."""
        super().__init__()
        self.set_collide(False)


class Item(Entity):
    """A special type of an Entity within the game. This is an abstract class."""
    def on_hit(self, game):
        """This function should raise the NotImplementedError."""
        raise NotImplementedError


class Key(Item):
    """A special type of Item within the game."""

    _id = KEY

    def on_hit(self, game):
        """What happened when the key is taken.

        Parameters:
            game(GameLogic):Current running game.
        """
        player = game.get_player()
        player.add_item(self)
        game.get_game_information().pop(player.get_position())


class MoveIncrease(Item):
    """A special type of Item within the game."""

    _id = MOVE_INCREASE

    def __init__(self, moves=5):
        """Parameters:
            moves(int): Extra moves the Player will begranted. Default value = 5
        """
        super().__init__()
        self._moves = moves

    def on_hit(self, game):
        """What happened when the MoveIncrease is taken.

        Parameters:
            game(GameLogic):Current running game.
        """
        player = game.get_player()
        player.change_move_count(self._moves)
        game.get_game_information().pop(player.get_position())


class Door(Entity):
    """A special type of Entity within the game."""
    _id = DOOR

    def on_hit(self, game):
        """What happened when player is at the door.

        Parameters:
            game(GameLogic):Current running game.
        """
        player = game.get_player()
        for item in player.get_inventory():
            if item.get_id() == KEY:
                game.set_win(True)
                return

        print("You don't have the key!")


class Player(Entity):
    """A special type of Entity within the game."""

    _id = PLAYER

    def __init__(self, move_count):
        """Parameters:
                move_count (int): Number of moves a Player can have for the given dungeon they are in
        """
        super().__init__()
        self._move_count = move_count
        self._inventory = []
        self._position = None


    def set_position(self, position):
        """Sets the position of the Player.

        Parameters:
            position(tuple): New position for the player
        """
        self._position = position
        
    def get_position(self):
        """(tuple) Returns the player's position."""
        return self._position

    def change_move_count(self, number):
        """Change the move count of player.

        Parameters:
             number(int): Number to be added to the Player’s move count.
        """
        self._move_count += number

    def moves_remaining(self):
        """(int)Returns an int representing how many moves the Player has left."""
        return self._move_count

    def add_item(self, item):
        """Adds the item to the Player’s Inventory

        Parameters:
            item(Entity): Items to be added to the Player's Inventory
        """
        self._inventory.append(item)

    def get_inventory(self):
        """Returns a list that represents the Player's inventory."""
        return self._inventory


class GameLogic:
    """GameLogic contains all the game information and how the game should play out."""
    def __init__(self, dungeon_name="game2.txt"):
        """Constructor of the GameLogic class.

        Parameters:
            dungeon_name (str): The name of the level.
        """
        self._dungeon = load_game(dungeon_name)
        self._dungeon_size = len(self._dungeon)
        self._player = Player(GAME_LEVELS[dungeon_name])
        self._game_information = self.init_game_information()
        self._win = False

    def get_positions(self, entity):
        """Returns a list of tuples containing all positions of a given Entity type.

        Parameters:
            entity (str): the id of an entity.

        Returns:
            (list<tuple<int, int>>): Returns a list of tuples representing the 
            positions of a given entity id.
        """
        positions = []
        for row, line in enumerate(self._dungeon):
            for col, char in enumerate(line):
                if char == entity:
                    positions.append((row, col))

        return positions

    def init_game_information(self):
        """(tuple)Return a dictionary containing the position and the corresponding Entity as the keys and values respectively."""
        player_pos = self.get_positions(PLAYER)[0]
        key_position = self.get_positions(KEY)[0]
        door_position = self.get_positions(DOOR)[0]
        wall_positions = self.get_positions(WALL)
        move_increase_positions = self.get_positions(MOVE_INCREASE)
        
        self._player.set_position(player_pos)

        information = {
            key_position: Key(),
            door_position: Door(),
        }

        for wall in wall_positions:
            information[wall] = Wall()

        for move_increase in move_increase_positions:
            information[move_increase] = MoveIncrease()

        return information

    def get_player(self):
        """(Player)Returns the Player object within the game."""
        return self._player

    def get_entity(self, position):
        """Returns an Entity in the given position in the dungeon.

        Parameters:
            position(tuple): Position of the entity.

        Returns:
            Entity: Returns an Entity in the given position.
        """
        return self._game_information.get(position)

    def get_entity_in_direction(self, direction):
        """Returns an Entity in the given direction of the Player’s position.

        Parameters:
            direction(str): direction moving towards

        Returns:
            Entity: Returns an Entity in the given position.
        """
        new_position = self.new_position(direction)
        return self.get_entity(new_position)

    def get_game_information(self):
        """(dict)Returns a dictionary containing the position and the corresponding Entity for the current dungeon."""
        return self._game_information

    def get_dungeon_size(self):
        """(int)Returns the width of the dungeon as an integer."""
        return self._dungeon_size

    def move_player(self, direction):
        """Update the Player’s position to place them one position in the given direction.

        Parameters:
            direction(str): direction moving towards
        """
        new_pos = self.new_position(direction)
        self.get_player().set_position(new_pos)

    def collision_check(self, direction):
        """
        Check to see if a player can travel in a given direction
        Parameters:
            direction (str): a direction for the player to travel in.

        Returns:
            (bool): False if the player can travel in that direction without colliding otherwise True.
        """
        new_pos = self.new_position(direction)
        entity = self.get_entity(new_pos)
        if entity is not None and not entity.can_collide():
            return True
        
        return not (0 <= new_pos[0] < self._dungeon_size and 0 <= new_pos[1] < self._dungeon_size)

    def new_position(self, direction):
        """Returns a tuple of integers that represents the new position of the player given the direction.

        Parameters:
            direction(str): direction moving towards

        Returns:
            tuple: New position given the direction.
        """
        x, y = self.get_player().get_position()
        dx, dy = DIRECTIONS[direction]
        return x + dx, y + dy

    def check_game_over(self):
        """(bool)Return True if the game has been lost and False otherwise."""
        return self.get_player().moves_remaining() <= 0

    def set_win(self, win):
        """Set the game’s win state to be True or False.

        Parameters:
            win(bool):Win state
        """
        self._win = win

    def won(self):
        """(bool)Return game’s win state."""
        return self._win
    
"""This is the end of model classes"""

"""This is the start of view classes"""

class AbstractGrid(tk.Canvas):
    """Provides base functionality for many of the view classes"""
    def __init__(self, master, rows, cols, width, height, **kwargs):
        """Though AbstractGrid is an abstract class, if it were to be instantiated,
        it would be as AbstractGrid(master, rows, cols, width, height, **kwargs)
        """
        super().__init__(width = width, height = height, **kwargs)
        
        self._master = master
        self._rows = rows
        self._cols = cols
        self._width = width
        self._height = height

        self._each_box_width = width/cols
        self._each_box_height = height/rows

        self.pack(side =tk.LEFT)

        
    def get_bbox(self, position):
        """Returns the bounding box for the (row, col) position.

        Parameters:
            position(tuple)

        Returns:
            tuple: Bounding box coordinates for given position.
        """
        y = position[0]
        x = position[1]
        
        top_x = x*self._each_box_width
        top_y = y*self._each_box_height
        
        bottom_x = (x+1)*self._each_box_width
        bottom_y = (y+1)*self._each_box_height
        
        return [top_x, top_y, bottom_x, bottom_y]
    
    def pixel_to_position(self, pixel):
        """Converts the x, y pixel position (in graphics units) to a (row, col) position.

        Parameters:
            pixel(tuple)

        Returns:
            tuple: position for given pixel.
        """
        x = pixel[0]
        y = pixel[1]
        
        col = x//self._each_box_width-1
        row = y//self._each_box_height-1
        
        if x%self._each_box_width != 0:
            col += 1
        if y%self._each_box_height != 0:
            row += 1
        return (row, col)
    
    def get_position_center(self, position):
        """ Gets the graphics coordinates for the center of the cell at the given (row, col) position.

        Parameters:
            position(tuple)

        Returns:
            tuple: center coordinates for given position.
        """
        bbox = self.get_bbox(position)
        top_x = bbox[0]
        top_y = bbox[1]
        bottom_x = bbox[2]
        bottom_y = bbox[3]

        center = ((top_x+bottom_x)/2,(top_y+bottom_y)/2)
        return center
    
    def draw_bounding_box(self, position,color):
        """ Draw block at the given (row, col) position, in given color.

        Parameters:
            position(tuple)
            color(str)

        Returns:
            rectangle: A rectangle at given position in given color.
        """ 
        pixel = self.get_bbox(position)
        x1 = pixel[0]
        y1 = pixel[1]
        x2 = pixel[2]
        y2 = pixel[3]
        self.create_rectangle(x1,y1,x2,y2,fill=color)
        
    def annotate_position(self, position, text):
        """ Annotates the cell at the given (row, col) position with the provided text.

        Parameters:
            position(tuple)
            text(str)

        Returns:
            Text: Text at given position.
        """ 
        center = self.get_position_center(position)
        x = center[0]
        y = center[1]
        self.create_text(x,y,fill="black",font="Times 10 italic bold",text=f"{text}")
        
        
class DungeonMap(AbstractGrid):
    """Where entities are drawn on the map using coloured
    rectangles at different (row, column) positions. """
    def __init__(self, master, size, width = 600, **kwargs):
        """The DungeonMap class should be
        instantiated as DungeonMap(master, size, width=600, **kwargs)
        """
        super().__init__(master = master, width = width, height = width, rows = size, cols = size, **kwargs)
        self._master = master
        self._size = size
        self._width = width
        self.pack(side =tk.LEFT)
                
    def draw_grid(self, dungeon, player_position):
        """ Draws the dungeon on the DungeonMap based on dungeon, and draws the player at the specified (row, col) position.

        Parameters:
            dungeon(GameLogic)
            player_position(tuple)

        Returns:
            Map: DungeonMap drawn based on given information.
        """
        key_position = dungeon.get_positions(KEY)[0]
        door_position = dungeon.get_positions(DOOR)[0]
        move_increase_positions = dungeon.get_positions(MOVE_INCREASE)
        wall_positions = dungeon.get_positions(WALL)

        if dungeon.get_game_information().get(key_position,'nope') != 'nope':
            self.draw_bounding_box(key_position,'yellow')
            self.annotate_position(key_position,'Key/Trash')
            
        self.draw_bounding_box(door_position,'red')
        self.annotate_position(door_position,'Door/Nest')
                
        self.draw_bounding_box(player_position,'mediumspringgreen')
        self.annotate_position(player_position,'Player/Ibis')
                
        for wall in wall_positions:
            self.draw_bounding_box(wall,'darkgrey')
            self.annotate_position(wall,'')
        for move_increase in move_increase_positions:
            if dungeon.get_game_information().get(move_increase,'nope') != 'nope':
                self.draw_bounding_box(move_increase,'orange')
                self.annotate_position(move_increase,'Move/Banana')
                
class AdvancedDungeonMap(DungeonMap):
    """AdvancedDungeonMap for task2&masters, incorporate images onto the map. """
    def __init__(self, master, size, width = 600, **kwargs):
        """Changes: introduce a list for images references."""
        super().__init__(master = master, size = size, width = width,**kwargs)
        self._master = master
        self._size = size
        self._width = width
        self._img_ref = []
        self.pack(side =tk.LEFT)
        
        
    def draw_bounding_box_advanced(self, position,image_path):
        """ Lay image('xxx/xxx.png') at the given (row, col) position.

        Parameters:
            image_path(str)
            position(tuple)

        Returns:
            Image: An image at given position.
        """ 
        width = int(self._each_box_width)
        height = int(self._each_box_height)
        image_resized = ImageTk.PhotoImage(Image.open(image_path).resize((width,height), Image.ANTIALIAS))
        pixel = self.get_position_center(position)
        x = pixel[0]
        y = pixel[1]
        image = self.create_image(x, y, image=image_resized)
        self._img_ref.append(image_resized)#Critcal:Keep references of images.
        
    def draw_grid_advanced(self, dungeon, player_position):
        """ Draws the dungeon on the AdvancedDungeonMap based on dungeon, and draws the player at the specified (row, col) position.

        Parameters:
            dungeon(GameLogic)
            player_position(tuple)

        Returns:
            Map: AdvancedDungeonMap drawn based on given information.
        """
        key_position = dungeon.get_positions(KEY)[0]
        door_position = dungeon.get_positions(DOOR)[0]
        move_increase_positions = dungeon.get_positions(MOVE_INCREASE)
        wall_positions = dungeon.get_positions(WALL)
        empty_positions = dungeon.get_positions(' ')
        original_player_pos = dungeon.get_positions(PLAYER)[0]
        
        if dungeon.get_game_information().get(key_position,'nope') != 'nope':
            self.draw_bounding_box_advanced(key_position,'images/empty.png')
            self.draw_bounding_box_advanced(key_position,'images/key.png')
        else:
            self.draw_bounding_box_advanced(key_position,'images/empty.png')
            
        if dungeon.get_game_information().get(original_player_pos,'nope') == 'nope':
            self.draw_bounding_box_advanced(original_player_pos,'images/empty.png')
            
        self.draw_bounding_box_advanced(door_position,'images/empty.png')    
        self.draw_bounding_box_advanced(door_position,'images/door.png')
        
        self.draw_bounding_box_advanced(player_position,'images/empty.png')        
        self.draw_bounding_box_advanced(player_position,'images/player.png')
        
        for move_increase in move_increase_positions:
            if dungeon.get_game_information().get(move_increase,'nope') != 'nope':
                self.draw_bounding_box_advanced(move_increase,'images/empty.png')
                self.draw_bounding_box_advanced(move_increase,'images/moveIncrease.png')
            else:
                if move_increase !=player_position:
                    self.draw_bounding_box_advanced(move_increase,'images/empty.png')
            

        for wall in wall_positions:
            self.draw_bounding_box_advanced(wall,'images/wall.png')
        for empty in empty_positions:
            if empty !=player_position:
                self.draw_bounding_box_advanced(empty,'images/empty.png')
            
        
            
        
class KeyPad(AbstractGrid):
    """A click-on control panel"""
    def __init__(self, master, width = 200,height = 100, **kwargs):
        """The KeyPad class should be instantiated as KeyPad(master, width=200, height=100, **kwargs).
"""
        super().__init__(master = master, width = width, height = height, rows = 2, cols = 3, **kwargs)
        self._master = master
        self._height = height
        self._width = width

        self.pack(side=tk.RIGHT)
        
        self.draw_bounding_box((0,1),'grey')
        self.annotate_position((0,1),'N')
        
        self.draw_bounding_box((1,0),'grey')
        self.annotate_position((1,0),'W')
        
        self.draw_bounding_box((1,1),'grey')
        self.annotate_position((1,1),'S')
        
        self.draw_bounding_box((1,2),'grey')
        self.annotate_position((1,2),'E')
        
class StatusBar(tk.Frame):
    """Hold status information"""
    def __init__(self, parent) :
        """Initialise the widget, with its subwidgets."""
        super().__init__(parent)
        self._parent = parent
        
class AdvancedStatusBar(StatusBar):
    """Advanced version for Masters"""
    def __init__(self, parent) :
        """Initialise the widget, with its subwidgets."""
        super().__init__(parent)
        self._parent = parent
        
"""This is the end of model classes"""

"""This is the start of controller classes"""    
class GameApp:
    """GameApp acts as a communicator between the GameLogic and the Display"""
    def __init__(self, master, task=TASK_ONE, dungeon_name="game2.txt"):
        """GameApp should be constructed with GameApp()."""
        
        self._task = task
        self._dungeon = dungeon_name
        self._game = GameLogic(dungeon_name)
        self._player_name =''
        #save status
        self._save_exist = False
        #score list status
        self._score_exist = False
        #score popup status
        self._score_popup = None
        #winner name status
        self._name_entry = None
        #player last status
        self._save_on_move = None
        
        self._master = master
        master.title("Key Cave Adventure Game")
        master.minsize(900, 600)
        
        #Bind keyboard input
        master.bind("<Key>",self.move)

        #Create top label
        self._top = tk.Label(self._master, text="Key Cave Adventure Game", font="Times 20 italic bold", bg = 'mediumspringgreen')
        self._top.pack(fill='x')
        
        #Check task first
        #For task one we only need a simple map:D
        if self._task == TASK_ONE:
            self._Dmap = DungeonMap(self._master, self._game.get_dungeon_size())
            self._Dmap.draw_grid(self._game, self._game.get_player().get_position())

        #For task 2&Master we need more than that
        else:
            #Menubar first
            menubar = tk.Menu(master)
            master.config(menu=menubar)

            filemenu = tk.Menu(menubar)
            menubar.add_cascade(label="File", menu=filemenu)
            filemenu.add_command(label="Save game", command=self.savegame)
            filemenu.add_command(label="Load game", command=self.loadgame)
            filemenu.add_command(label="New game", command=self.newgame)
            filemenu.add_command(label="Quit", command=self.quitgame)
            
            #Then the status bar
            #Check task to confirm whether we need advancedbar
            if self._task == MASTERS:
                filemenu.add_command(label="High scores", command=self.highscores)
                self._settings = AdvancedStatusBar(self._master)
                self._settings.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

            if self._task == TASK_TWO:
                self._settings = StatusBar(self._master)
                self._settings.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

            #Set up the minor functions in status bar

            #New game&quit button
            self._button_frame = tk.Frame(self._settings)
            self._button_frame.pack(side=tk.LEFT,padx = 30)
            self._new_game_button = tk.Button(self._button_frame, text="New game",command=self.newgame)
            self._new_game_button.pack(pady = 10)
            self._quit_button = tk.Button(self._button_frame, text="Quit",command=self.quitgame)
            self._quit_button.pack(pady = 10)

            #Timer section
            self._time_frame = tk.Frame(self._settings)
            self._time_frame.pack(side=tk.LEFT,padx = 30)
            timer = ImageTk.PhotoImage(Image.open('images/clock.png').resize((50,50), Image.ANTIALIAS))
            self._time_pic_label = tk.Label(self._time_frame, image = timer)
            self._time_pic_label.image = timer#keep a reference
            self._time_pic_label.pack(side=tk.LEFT)
            self._timer_frame = tk.Frame(self._time_frame)
            self._timer_frame.pack(side=tk.RIGHT,padx = 10)
            self._timer_text_label = tk.Label(self._timer_frame, text="Time elpased")
            self._timer_text_label.pack(pady = 10)
            self._timer_label = tk.Label(self._timer_frame, text=f"0m 0s")
            self._timer_label.pack(pady = 10)
            self._timer_start = True
            self._time_passed = 0
            self.timer()

            #Movement counter
            self._moves_frame = tk.Frame(self._settings)
            self._moves_frame.pack(side=tk.LEFT,padx = 30)
            moves = ImageTk.PhotoImage(Image.open('images/lightning.png').resize((50,50), Image.ANTIALIAS))
            self._moves_pic_label = tk.Label(self._moves_frame, image = moves)
            self._moves_pic_label.image = moves#keep a reference
            self._moves_pic_label.pack(side=tk.LEFT)
            self._moves_counter_frame = tk.Frame(self._moves_frame)
            self._moves_counter_frame.pack(side=tk.RIGHT,padx = 10)
            self._moves_counter_text_label = tk.Label(self._moves_counter_frame, text="Moves left")
            self._moves_counter_text_label.pack(pady = 10)
            self._moves = self._game.get_player().moves_remaining()
            self._moves_counter_label = tk.Label(self._moves_counter_frame, text=f"{self._moves} moves remaining")
            self._moves_counter_label.pack(pady = 10)

            #Check if it is Master to confirm whether we need live section.
            if self._task == MASTERS:
                self._life_frame = tk.Frame(self._settings)
                self._life_frame.pack(side=tk.LEFT,padx = 30)
                life = ImageTk.PhotoImage(Image.open('images/lives.png').resize((50,50), Image.ANTIALIAS))
                self._life_pic_label = tk.Label(self._life_frame, image = life)
                self._life_pic_label.image = life#keep a reference
                self._life_pic_label.pack(side=tk.LEFT)
                self._life_counter_frame = tk.Frame(self._life_frame)
                self._life_counter_frame.pack(side=tk.RIGHT,padx = 10)
                self._life_left = 3
                self._life_counter_label = tk.Label(self._life_counter_frame, text=f"Lives remaining: {self._life_left}")
                self._life_counter_label.pack(pady = 10)
                self._use_life_button = tk.Button(self._life_counter_frame, text="Use life",command=self.use_life)
                self._use_life_button.pack(pady = 10)

            #Draw the map for task2&master
            self._Dmap = AdvancedDungeonMap(self._master, self._game.get_dungeon_size())
            self._Dmap.draw_grid_advanced(self._game, self._game.get_player().get_position())
        
        #Keypad           
        self._keypad = KeyPad(self._master)
        self._keypad.bind("<Button-1>",self.press_keypad)
        
    def newgame(self):
        """destory the master then restart the game"""
        self._master.destroy()
        main()
        
    def quitgame(self):
        """For task2&master. Ask the user whether or not the game should be closed."""
        messagebox = tk.messagebox.askquestion ('Quit game','ARE YOU SURE ABOUT DAT?',icon = 'warning')
        if messagebox == 'yes':
            self._master.destroy()
        
    def savegame(self):
        """For task2&master. Save critical information in .txt format."""
        files = [ ('Text Document', '*.txt')] 
        f = asksaveasfile(mode='w', filetypes = files, defaultextension=".txt")
        if f is None: # asksaveasfile return `None` if dialog closed with "cancel".
            return
        #save all the info blahblahblah
        current_dungeon = self._dungeon
        current_time_used = self._time_passed
        player_pos = self._game.get_player().get_position()
        current_moves = self._game.get_player().moves_remaining()

             
        #check key&move increase in the position or not
        key_position = self._game.get_positions(KEY)[0]
        key = True
        if self._game.get_game_information().get(key_position,'nope') == 'nope':
            key = False
            
        move_increase_position = self._game.get_positions(MOVE_INCREASE)[0]
        move_inc = True     
        if self._game.get_game_information().get(move_increase_position,'nope') == 'nope':
            move_inc = False
            
        #check the task to decide whether life should be included.
        if self._task == MASTERS:
            current_life = self._life_left
        else:
            current_life = 'placeholder'
        
        #Set up the text we need to save
        text2save = f'{current_dungeon}\n{current_time_used}\n{current_life}\n{current_moves}\n{player_pos}\n{key}\n{move_inc}'
        
        f.write(text2save)
        f.close()
        
    def quick_save_on_move(self):
        """For master task. quicksave on every move."""
        #Basically the same function as save game.
        current_dungeon = self._dungeon
        player_pos = self._game.get_player().get_position()  
        current_time_used = self._time_passed
        current_moves = self._game.get_player().moves_remaining()
        
        key_position = self._game.get_positions(KEY)[0]
        key = True
        if self._game.get_game_information().get(key_position,'nope') == 'nope':
            key = False
        
        move_increase_position = self._game.get_positions(MOVE_INCREASE)[0]
        move_inc = True    
        if self._game.get_game_information().get(move_increase_position,'nope') == 'nope':
            move_inc = False   
        
        self._save_on_move = [current_dungeon,current_time_used,current_moves,player_pos,key,move_inc]
        
    def loadgame(self):
        """For task2&masters. load the saves"""
        files = [ ('Text Document', '*.txt')]
        filename = askopenfilename(initialdir = "/",title = "Select file",filetypes = files)
        file_info = []

        try:
            with open(filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    file_info.append(line)
            self._save_exist = True
            
        except IOError:
            #Stop it if sth wrong happened.
            self._save_exist = False
            
        if self._save_exist == True:
            #Break down the stored information and update each of them ingame.

            #Dungeon update
            last_dungeon = file_info[0]
            self._dungeon = last_dungeon
            self._game = GameLogic(last_dungeon)

            #timer update
            last_time_used = int(file_info[1])
            self._time_passed = last_time_used
            min_passed = last_time_used//60
            sec_passed = last_time_used%60
            self._timer_label.config(text=f"{min_passed}m {sec_passed}s")

            #move counter update
            last_moves = int(file_info[3])
            self._game.get_player()._move_count = last_moves
            self._moves_counter_label.config(text=f"{last_moves} moves remaining")
            
            #life update for task Masters
            if self._task == MASTERS:
                last_life = int(file_info[2])
                self._life_left = last_life
                self._life_counter_label.config(text=f"Lives remaining: {self._life_left}")

                    
                
            #Player position update    
            last_player_pos = (int(file_info[4][1]),int(file_info[4][4]))
            self._game.get_player().set_position(last_player_pos)

            #key status update
            last_key_exist = file_info[5]
            key_position = self._game.get_positions(KEY)[0]
            if last_key_exist == 'False':
                self._game.get_game_information().pop(key_position)
                self._game.get_player().add_item(Key())
                
            #Moveincrease status update    
            last_move_inc_exist = file_info[6]
            move_increase_position = self._game.get_positions(MOVE_INCREASE)[0]
            if last_move_inc_exist == 'False':
                self._game.get_game_information().pop(move_increase_position)
                
            #After all critical information are loaded, redraw the map.
            self._Dmap.delete(tk.ALL)
            self._Dmap.draw_grid_advanced(self._game, self._game.get_player().get_position())
        else:
            tk.messagebox.showerror(f'{INVALID}',"You didn't select which file to load")
        
    def record_scores(self):
        """For task Masters. Popup after winning."""
        self._score_popup = tk.Toplevel()
        self._score_popup.title("Please leave your record here!")
        
        score_label = tk.Label(self._score_popup, text=f'You won in {self._time_passed//60}m {self._time_passed%60}s. Enter your name please', font="Times 10 italic bold")
        score_label.pack(pady = 5)
        
        self._name_entry = tk.Entry(self._score_popup)
        self._name_entry.pack(fill=tk.X,pady = 5,padx = 10)

        #bind mulitple function on enter button.
        enter_button = tk.Button(self._score_popup, text="Enter",command=lambda:[self.savescores(),self._score_popup.destroy(),self.call_messagebox('won')])
        enter_button.pack(pady = 5,padx = 10)

        
        
    def savescores(self):
        """Save the input record."""
        self._player_name = self._name_entry.get()
        
        name = self._player_name
        score = self._time_passed
        text2save = f'{name},{score}\n'
        
        record_file = open("record.txt","a")
        record_file.write(text2save)
        record_file.close()
           
        
    def highscores(self):
        """Load the high score file&display it"""
        score_window = tk.Toplevel()
        score_window.title("High scores")
        record_info = []
        
        try:
            with open("record.txt", "r") as file:
                for line in file:
                    line = line.strip()
                    record_info.append(line)
            self._score_exist = True
            
        except IOError:
            self._score_exist = False
        
        check_score_list =[]
        name = ''
        score = 0
        winner_list ={}


        if self._score_exist != False:
            number_of_records = len(record_info)
            for line in record_info:
                line_text = line.split(",")
                mark = int(line_text[1])
                check_score_list.append(mark)
            #Set up the score list and sort it in advance.
            check_score_list.sort()
            
            for record in record_info:
                individual = record.split(",")
                name = individual[0]
                score = int(individual[1])
                minute = score//60
                second = score%60
                score_text =f"{minute}m {second}s"

                if number_of_records >=3 and score in [check_score_list[0],check_score_list[1],check_score_list[2]] :
                    winner_list[name] = score
                if number_of_records ==2 or 1:
                    winner_list[name] = score
            #Sort the winner_list dictionary by item's value.       
            winner_list = {k: v for k, v in sorted(winner_list.items(), key=lambda item: item[1])}

        else:
            #placeholder for no file.
            winner_list ={'Nobody':'literally nobody'}
            
        label_top = tk.Label(score_window, text="High Scores",bg = 'mediumspringgreen',font="Times 10 italic bold",)
        label_top.pack(fill='x', pady=5)
        
        record_count = 0
        names = list(winner_list)
        for name in names:
            if self._score_exist != False:
                if record_count < 3:
                    label_record = tk.Label(score_window, text=f"{name}: {winner_list[name]//60}m {winner_list[name]%60}s")
                    label_record.pack(fill='x', padx=50, pady=5)
                    record_count += 1
            else:
                label_record = tk.Label(score_window, text=f"{name}: {winner_list[name]}")
                label_record.pack(fill='x', padx=50, pady=5)

        button_close = tk.Button(score_window, text="Done", command=score_window.destroy)
        button_close.pack()
        
        

    
    def timer(self):
        """Timer function for status bar."""
        if self._timer_start:
            self._time_passed += 1
            min_passed = self._time_passed//60
            sec_passed = self._time_passed%60
            self._timer_label.config(text=f"{min_passed}m {sec_passed}s")
            self._master.after(1000,self.timer)
            
    def use_life(self):
        """For task Masters, use life to restore the game to last status.Basically the same function as loadgame"""
        last_move_information = self._save_on_move
        
        if self._life_left >= 1:
            self._life_left -= 1
            self._life_counter_label.config(text=f"Lives remaining: {self._life_left}")
            
            last_dungeon = last_move_information[0]
            self._dungeon = last_dungeon
            self._game = GameLogic(last_dungeon)
            
            last_time_used = last_move_information[1]
            self._time_passed = last_time_used

            last_moves = last_move_information[2]
            self._game.get_player()._move_count = last_moves
            self._moves_counter_label.config(text=f"{last_moves} moves remaining")
            
            last_player_pos = (last_move_information[3][0],last_move_information[3][1])
            self._game.get_player().set_position(last_player_pos)
        
            last_key_exist = last_move_information[4]
            key_position = self._game.get_positions(KEY)[0]
            if last_key_exist == False:
                self._game.get_game_information().pop(key_position)
                self._game.get_player().add_item(Key())
                
            last_move_inc_exist = last_move_information[5]    
            move_increase_position = self._game.get_positions(MOVE_INCREASE)[0]
            if last_move_inc_exist == False:
                self._game.get_game_information().pop(move_increase_position)

            self._Dmap.delete(tk.ALL)
            self._Dmap.draw_grid_advanced(self._game, self._game.get_player().get_position())

        else :
            tk.messagebox.showinfo('No life left','Try something else')
            
            
    
    def press_keypad(self,event):
        """Keypad to control the direction"""
        direction = ''
        click = self._keypad.pixel_to_position((event.x,event.y))
        if click == (0,1):
            direction = 'w'
            
        if click == (1,0):
            direction = 'a'
            
        if click == (1,1):
            direction = 's'
            
        if click == (1,2):
            direction = 'd'

        event.char = direction
        self.move(event)
    def call_messagebox(self,state):
        """For task 2, call the messagebox when game is over/won."""
        messagebox = tk.messagebox.askquestion (f'You {state}!',f'You have finished the level with a score of {self._time_passed//60}m {self._time_passed%60}s.\nWould you like to play again?',icon = 'warning')
        if messagebox == 'yes':
            self.newgame()
        else:
            self.quitgame()

    def move(self,event):
        """Main function for progamer move."""
        
        player = self._game.get_player()
        
        if self._task == MASTERS:
            #check if we need to save information for life function
            self.quick_save_on_move()
            
        if event.char in ['w','a','s','d']:
            direction = event.char
            player.change_move_count(-1)
            moves = player.moves_remaining()
                        
            # if player does not collide move them
            if not self._game.collision_check(direction):
                #In order to redraw the map on every move, we need to delete the pre-existing map.
                self._Dmap.delete(tk.ALL)
                
                self._game.move_player(direction)
                entity = self._game.get_entity(player.get_position())
                
                if self._task == TASK_ONE:
                    #redraw the map
                    self._Dmap.draw_grid(self._game, player.get_position())
                else:
                    #redraw the map for task2&Masters, also configure the move counter.
                    self._moves_counter_label.config(text=f"{moves} moves remaining")
                    self._Dmap.draw_grid_advanced(self._game, player.get_position())
                # process on_hit and check win state
                
                if entity is not None:
                    entity.on_hit(self._game)
                    if player.get_position() in self._game.get_positions(MOVE_INCREASE):
                        if self._task == TASK_ONE:
                            self._Dmap.draw_grid(self._game, player.get_position())
                        else:
                            self._moves_counter_label.config(text=f"{moves+5} moves remaining")
                            self._Dmap.draw_grid_advanced(self._game, player.get_position())
                    if self._game.won():
                        if self._task == TASK_ONE:
                            #for task one we only need to pop info
                            tk.messagebox.showinfo('You won',f'{WIN_TEXT}')
                            self._master.destroy()
                        else:
                            #for task2&masters we need to stop timer and prepare different popup.
                            self._timer_start = False
                            if self._task == MASTERS:
                                self.record_scores()
                            if self._task == TASK_TWO:
                                self.call_messagebox('won')
            else:
                tk.messagebox.showerror(f'{INVALID}','This is a wall in the way!')
                if self._task != TASK_ONE:
                    self._moves_counter_label.config(text=f"{moves} moves remaining")
                
            if self._game.check_game_over():
                if self._task == TASK_ONE:
                    tk.messagebox.showinfo('You lost',f'{LOSE_TEXT}')
                    self._master.destroy()
                else:
                    self._timer_start = False
                    self.call_messagebox('lost')

"""This is the end of controller classes"""
                

            
        


def main():
    root = tk.Tk()
    app = GameApp(root, 3,'game2.txt')
    root.mainloop()

if __name__ == "__main__":
    main()
