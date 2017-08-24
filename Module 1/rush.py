from PIL import Image, ImageDraw, ImageFont
from copy import copy, deepcopy
import cProfile


BOARD_1 = [
    [0,2,2,2],
    [0,0,4,3],
    [0,3,4,2],
    [0,4,1,2],
    [1,2,0,2],
    [1,4,2,2]
]

BOARD_2 = [
    [0,1,2,2],
    [0,0,5,3],
    [0,1,3,2],
    [0,3,0,2],
    [1,0,2,3],
    [1,2,0,2],
    [1,3,1,2],
    [1,3,3,3],
    [1,4,2,2],
    [1,5,0,2],
    [1,5,2,2]
]

BOARD_3 = [
    [0,2,2,2],
    [0,0,4,2],
    [0,0,5,2],
    [0,2,5,2],
    [0,4,0,2],
    [1,0,0,3],
    [1,1,1,3],
    [1,2,0,2],
    [1,3,0,2],
    [1,4,2,2],
    [1,4,4,2],
    [1,5,3,3]
]

BOARD_4 = [
    [0,0,2,2],
    [0,0,1,3],
    [0,0,5,2],
    [0,1,0,2],
    [0,2,3,2],
    [0,3,4,2],
    [1,0,3,2],
    [1,2,4,2],
    [1,3,0,3],
    [1,4,0,2],
    [1,4,2,2],
    [1,5,2,2],
    [1,5,4,2]
]

BOARD_5 = [
    [0,2,2,2],  #red
    [1,0,1,2],  #1
    [1,1,4,2],  #2
    [1,2,3,2],  #3
    [1,3,0,2],  #4
    [1,4,0,3],  #5
    [1,5,0,3],  #6
    [0,0,0,3],  #13
    [0,1,1,2],  #14
    [0,0,3,2],  #16
    [0,4,4,2],  #17
    [0,2,5,2],  #18
    [0,4,5,2]
]




#Use pillow to paint a board with some text and a number
def paintboard(board, iteration):
    im = Image.new("RGB", (6*50, 7*50), "white")
    draw = ImageDraw.Draw(im)
    y = 0
    for row in range(6):
        x = 0
        for col in range(6):
            draw.ellipse([(x+20, y+20), (x+30, y+30)], (0,0,0))
            x = x + 50
        y = y + 50
    colors = {1: "#F44336",2: "#E91E63",3: "#9C27B0",4: "#673AB7",5: "#3F51B5",6: "#2196F3",7: "#03A9F4",8: "#00BCD4",9: "#009688",10: "#4CAF50",11: "#8BC34A",12: "#CDDC39",13: "#FFEB3B"}
    for car in board:
        color = colors[board.index(car)+1]
        x = 50*car[1]
        y = 50*car[2]
        deltax = 0
        deltay = 0
        if not car[0]:    #horizontal
            deltax = 50
        else:           #vertical
            deltay = 50
        for i in range(car[3]):
            draw.rectangle([x, y, x+50, y+50], color)
            x = x + deltax
            y = y + deltay
    text = "Iteration #"+ str(iteration)
    draw.text((10, 310), text,(0,0,0))
    im.save("/home/espen/Desktop/output/" + str(iteration) + ".png")

#Calculate the coordinates occupied by a given car
def get_car_coords(car):
    coords = []
    x = car[1]
    y = car[2]
    deltax = 0
    deltay = 0
    if car[0]:    #vertical
        deltay = 1
    else:           #horizontal
        deltax = 1
    for i in range(car[3]):
        coords.append((x,y))
        x = x + deltax
        y = y + deltay
    return coords



#Checks if a certain coordinate is occupied by a car
def is_blocked(x, y, board):
    if x < 0 or x > 5 or y < 0 or y > 5:
        return True
    for car in board:
        if (x,y) in get_car_coords(car):
            return True
    return False

#Takes a car and a board and calculates the possible moves of that car in the board
def calculate_options(car, board):
    new_boards = []
    coords = get_car_coords(car)
    index = board.index(car)
    if car[0]:  #vertical
        if not is_blocked(coords[0][0],coords[0][1]-1, board): #move up
            nb = deepcopy(board)
            nb[index][2] = nb[index][2]-1
            new_boards.append(nb)
        if not is_blocked(coords[len(coords)-1][0],coords[len(coords)-1][1]+1, board): #move down
            nb = deepcopy(board)
            nb[index][2] = nb[index][2]+1
            new_boards.append(nb)
    else:       #horizontal
        if not is_blocked(coords[0][0]-1,coords[0][1], board): #move right
            nb = deepcopy(board)
            nb[index][1] = nb[index][1]-1
            new_boards.append(nb)
        if not is_blocked(coords[len(coords)-1][0]+1,coords[len(coords)-1][1], board): #move left
            nb = deepcopy(board)
            nb[index][1] = nb[index][1]+1
            new_boards.append(nb)
    return new_boards

#For each car in the board, calculate the moves it can do and return them as a list
def get_neighbours(board):
    neighbours = []
    for car in board:
        neighbours.extend(calculate_options(car, board))
    return neighbours

#Check if red car is in winning position
def is_won(board):
    return board[0][1] + board[0][3] -1 == 5

#Our best attempt at a heuristic function. Turns out, its not good...
def h(board):
    n = 0
    n = n + 5 - board[0][1]+1       #how many moves to get red car to goal
    for i in range(board[0][1]+2, 6):   #how many of those are blocked?
        if is_blocked(i, 2, board):
            n = n + 1
    return n


#Iterates through the open set and returns the best board in it
def get_best_board(open_set, cost):
    bestcost = float("inf")
    bestboard = None
    for board in open_set:
        if cost[hash_board(board)] + h(board)  < bestcost:
            bestboard = board
            bestcost = cost[hash_board(board)]
    return bestboard

#Python cannot hash lists, so to be able to use them as keys in dictionaries
#we created a custom hash function
def hash_board(board):
    return tuple(sum(board, []))

#Create a history of boards to reach the current board. Used to visualize the process
#Can calculate how many moves to reach goal, as well display all steps
def backtrack(node, parent, display):
    history = []
    while hash_board(node) in parent.keys():
        history.append(node)
        node = parent[hash_board(node)]
    history.reverse()
    print "Optimal game:", len(history), "moves"
    if display:
        counter = 1
        for board in history:
            paintboard(board, counter)
            counter = counter + 1





#Generic A* code
def astar(board, display):
    closed_set = []
    open_set = [board]
    parent = {}
    cost = {hash_board(board): 0}
    counter = 0
    while open_set:
        counter = counter +1
        current = get_best_board(open_set, cost)
        if is_won(current):
            print "Used", counter, "iterations to compute result"
            backtrack(current, parent, display)
            return True
        open_set.remove(current)
        closed_set.append(current)
        for neighbour in get_neighbours(current):
            if neighbour in closed_set:
                continue
            tentative_score = cost[hash_board(current)] + 1
            if neighbour not in open_set:
                open_set.append(neighbour)
            elif tentative_score >= cost[hash_board(neighbour)]:
                continue
            parent[hash_board(neighbour)] = current
            cost[hash_board(neighbour)] = tentative_score

    return False



#print astar(BOARD_3, False)
cProfile.run('astar(BOARD_5, True)')    #run the astar() function with profiling tools