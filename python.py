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

def next_turn():

def change_directions():

def check_collisions():

def game_over():

def reset_state(): 

def restart_game(): 

def start_game():

