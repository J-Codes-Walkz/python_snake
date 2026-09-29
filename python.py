import tkinter as tk
import random

# Create the main window
root = tk.Tk()
root.title("My Snake Game")
root.geometry("400x400")

#Constants
GAME WIDTH = 400
GAME HEIGHT = 400   
DELAY_MS = 100
SPACE_SIZE = 20
BODY_PARTS = 3
SNAKE_COLOR = "#0E093D"
FOOD_COLOR = "#1EE921"
BACKGROUND_COLOR = "#000000"
INITIAL_DIRECTION = 'Right'

COLS = GAME WIDTH // SPACE_SIZE
ROWS = GAME HEIGHT // SPACE_SIZE    
TOTAL CELLS = COLS * ROWS

OPPOSITES = ("Left", "Right"), ("Up", "Down")

#Game state (Start game / Restart game)
window = None    
canvas = None 
label = None 
food = None 
score = 0 
direction = INITIAL_DIRECTION
next_direction = INITIAL_DIRECTION 
game_running = false 



#Class Snake 
class snake: 
    def __init__(self):
        self.coordinates = [] 
        self.squares = []

        start_x = (COLS // 2) * SPACE_SIZE
        start_y = (ROWS // 2) * SPACE_SIZE 

        #Head first, body trailing to the left (snake moving right)
        for i in range(BODY_PARTS):
            self.coordinates.append((start_x - i * SPACE_SIZE, start_y))

            for x, y in self.coordinates:
                square = canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR, tag="snake")
                self.squares.append(square)
            


class food: 
    def __init__(self):
        x = random.randint(0, COLS - 1) * SPACE_SIZE
        y = random.randint(0, ROWS - 1) * SPACE_SIZE

        self.coordinates = (x, y)

        canvas.create_diamond(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=FOOD_COLOR, tag="food")

#Functions
def create_food(): 
    occupied = {tuple(c) for c in snake.coordinates} 
    free_cells = [ 
        (cold * SPACE_SIZE, ROW * SPACE_SIZE) for COL in range(COLS) for ROW in range(ROWS) if (COL * SPACE_SIZE, ROW * SPACE_SIZE) not in occupied 
    ]
        if not free_cells:
            return None
    x, y = random.choice(free_cells)
    return food(x, y)


    

def next_turn(snake, food):
    global direction, score,

#Apply the requested direction once per tick 
direction = next_direction
 x, y = snake.coordinates[0]
if direction == "Up":
    y -= SPACE_SIZE
elif direction == "Down":
    y += SPACE_SIZE
elif direction == "Left":
    x -= SPACE_SIZE
elif direction == "Right":
    x += SPACE_SIZE     

snake.coordinates.insert(0, (x, y))



def change_directions():

def check_collisions():

def game_over():

def reset_state(): 

def restart_game(): 

def start_game():

