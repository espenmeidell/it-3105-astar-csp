import numpy as np
import sys
from termcolor import colored
from collections import deque
from copy import copy, deepcopy
sys.path.append('../')
from astar import astar
import itertools
import cProfile

'''
        Read specifications from input
'''

first_line = sys.stdin.readline().split(" ")
number_of_cols = int(first_line[0].strip())
number_of_rows = int(first_line[1].strip())

row_specs = []
col_specs = []

row_counter = 0
for line in sys.stdin:
    str_array = line.split(" ")
    int_array = map(int, str_array)
    if row_counter < number_of_rows:
        row_counter += 1
        row_specs.append(int_array)
    else:
        col_specs.append(int_array)

row_specs.reverse()

'''
        Functions to create variables, domains and
        constraints for the specifications
'''

# for example: [1,2] results in the following list: [1,0,1,1]
def generate_minimum_placement(spec):
    insert_positions = [0]
    result = []
    for item in spec:
        result.extend([1] * item)
        result.append(0)
        insert_positions.append(len(result) -1)
    result.pop()
    return (result, insert_positions)


def create_domain(length, specifications):

    min_placement, insert_indices = generate_minimum_placement(specifications)
    domain = []

    combinations = itertools.combinations_with_replacement(insert_indices, length - len(min_placement))
    for c in combinations:
        result = min_placement[:]
        insert_positions = list(c)
        insert_positions.sort()
        offset = 0
        for index in insert_positions:
            result.insert(index + offset, 0)
            offset += 1
        domain.append(result)
    return domain


def create_variables(specifications, is_row, target_length):
    variables = []
    for (i, spec) in enumerate(specifications):
        variable_name = "R" + str(i) if is_row else "C" + str(i)
        domains[variable_name] = create_domain(target_length, spec)
        variables.append(variable_name)
    return variables

'''
        Define the variables, domains and constraint pairs
'''

domains = {}

variables = create_variables(row_specs, True, number_of_cols)
variables.extend(create_variables(col_specs, False, number_of_rows))

constraint_pairs = list(itertools.product( filter(lambda v: v[0] == 'R', variables)
                                         , filter(lambda v: v[0] == 'C', variables)))
constraint_pairs.extend(itertools.product( filter(lambda v: v[0] == 'C', variables)
                                         , filter(lambda v: v[0] == 'R', variables)))


'''
        Utility functions
'''

def is_row(variable):
    return variable[0] == "R"

def get_index_from_variable(variable):
    return int(variable[1:])


def print_result(variables, domain):
    rows = filter(lambda v: is_row(v), variables)
    print colored(' ', 'white', attrs=['reverse', 'blink']) * (number_of_cols * 2 + 3)
    for row in rows:
        print colored(' ', 'white', attrs=['reverse', 'blink']),
        for c in domain[row][0]:
            if c:
                print colored(' ', 'red', attrs=['reverse', 'blink']),
            else:
                print ' ',
        print colored(' ', 'white', attrs=['reverse', 'blink'])
    print colored(' ', 'white', attrs=['reverse', 'blink']) * (number_of_cols * 2 + 3)

'''
        A* Functions
'''

def find_successor(open_set, cost, heuristic):
    bestcost = float("inf")
    bestboard = None
    for board in open_set:
        if heuristic(board) < bestcost:
            bestboard = board
            bestcost = heuristic(board)
    return bestboard

# Create successor state by creating new triples where the domain is cloned and reduced
def generate_successors(current):
    successors = []
    for var in current[0]:
        for p in current[1][var]:
            child_domain = deepcopy(current[1])
            child_domain[var] = [p]
            # Reduce domain of successors
            queue = deque([])
            for c in current[2]:
                if var == c[1]:
                    queue.append(c)
            domain_filtering_loop(queue, child_domain, current[2])
            # Only retain successor if it is a legal state
            if (all(len(child_domain[v]) > 0 for v in current[0])):
                successors.append((current[0], child_domain, current[2]))
    return successors

# The sum of the length of the domains in the current state
def heuristic(state):
    return sum(map(lambda d: len(d), state[1].values()))

# Check if the domain length for each variable is 1
def is_terminal(state):
    return len(state[0]) == len(filter(lambda v: len(v) == 1, state[1].values()))

# Create a hash of the domain
def hash_function(s):
    return str(s[1])

'''
        CSP Functions
'''

def check_constraint(row, row_index, col, col_index):
    return row[col_index] == col[row_index]

def revise(X, Y, domains):
    new_domain = []
    for dX in domains[X]:
        for dY in domains[Y]:
            if is_row(X):
                if check_constraint(dX, get_index_from_variable(X), dY, get_index_from_variable(Y)):
                    if dX not in new_domain:
                        new_domain.append(dX)
                    continue
            else:
                if check_constraint(dY, get_index_from_variable(Y), dX, get_index_from_variable(X)):
                    if dX not in new_domain:
                        new_domain.append(dX)
                    continue
    reduced = len(domains[X]) > len(new_domain)
    domains[X] = new_domain
    return reduced

def domain_filtering_loop(queue, domains, constraints):
    while queue:
        X, Y = queue.popleft()
        reduced = revise(X, Y, domains)
        if reduced:
            for Ck in constraints:
                if X == Ck[1]:
                    queue.append(Ck)

def solve(variables, domains, constraints):
    queue = deque([])
    for c in constraints:
        queue.append(c)

    domain_filtering_loop(queue, domains, constraints)

    if len(filter(lambda v: len(domains[v]) > 1, variables)) != 0:    # are all domains reduced to 1
        result = astar((variables, domains, constraints)
                      , find_successor
                      , generate_successors
                      , heuristic
                      , is_terminal
                      , hash_function)
        print_result(result[1][0], result[1][1])
    else:
        print_result(variables, domains)



cProfile.run('solve(variables, domains, constraint_pairs)')
