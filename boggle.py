# boggle
import numpy as np
import sys

import string
import random
import copy
import pickle
from pathlib import Path
import json
import argparse

dice = [
    ['L', 'R', 'Y', 'T', 'T', 'E'],
    ['V', 'T', 'H', 'R', 'W', 'E'],
    ['E', 'G', 'H', 'W', 'N', 'E'],
    ['S', 'E', 'O', 'T', 'I', 'S'],
    ['A', 'N', 'A', 'E', 'E', 'G'],
    ['I', 'D', 'S', 'Y', 'T', 'T'],
    ['O', 'A', 'T', 'T', 'O', 'W'],
    ['M', 'T', 'O', 'I', 'C', 'U'],
    ['A', 'F', 'P', 'K', 'F', 'S'],
    ['X', 'L', 'D', 'E', 'R', 'I'],
    ['H', 'C', 'P', 'O', 'A', 'S'],
    ['E', 'N', 'S', 'I', 'E', 'U'],
    ['Y', 'L', 'D', 'E', 'V', 'R'],
    ['Z', 'N', 'R', 'N', 'H', 'L'],
    ['N', 'M', 'I', 'H', 'U', 'Qu'],
    ['O', 'B', 'B', 'A', 'O', 'J'],
]
def get_board():
    ldice = copy.copy(dice)
    board = []
    while True:
        if len(ldice) == 0:
            break
        die = random.choice(ldice)
        ldice.remove(die)
        letter = random.choice(die).lower()
        board.append(letter)
    board = np.array(board)
    board = board.reshape((4, 4))
    return board

def add_letter_combos(letter_combos, word):
    n = len(word)
    if n == 1:
        return
    if n==2 or n==3 or n==4 or n==5 or n==6:
        letter_combos.add(word)
        return
    word = np.array(list(word), dtype='<U1')
    combined2 = np.array((word[:-1], word[1:])).T
    combined3 = np.array((word[:-2], word[1:-1], word[2:])).T
    combined4 = np.array((word[:-3], word[1:-2], word[2:-1], word[3:])).T
    combined5 = np.array((word[:-4], word[1:-3], word[2:-2], word[3:-1], word[4:])).T
    combined6 = np.array((word[:-5], word[1:-4], word[2:-3], word[3:-2], word[4:-1], word[5:])).T
    
    combined2 = np.apply_along_axis(lambda x: ''.join(x), 1, combined2)
    combined3 = np.apply_along_axis(lambda x: ''.join(x), 1, combined3)
    combined4 = np.apply_along_axis(lambda x: ''.join(x), 1, combined4)
    combined5 = np.apply_along_axis(lambda x: ''.join(x), 1, combined5)
    combined6 = np.apply_along_axis(lambda x: ''.join(x), 1, combined6)
    for combined in [combined2, combined3, combined4, combined5, combined6]:
        for x in combined:
            letter_combos.add(x)
        
def get_dictionary():
    base = "dictionary"
    pkl = f"{base}.pkl"
    txt = f"{base}.txt"
    if Path(pkl).exists():
        with open(pkl, "rb") as f:
            return pickle.load(f)
    sys.stderr.write("Creating dictionary pickle...")
    sys.stderr.flush()
    maxlen = 0
    word_list = set()
    used_letter_combos = set()
    letter_combos = {}
    with open(txt, 'r') as file:
        for line in file:
            l = line.strip()
            n = len(l)
            if n > maxlen:
                maxlen = n
            word_list.add(l)
            add_letter_combos(used_letter_combos, l)
    with open(pkl, "wb") as f:
        pickle.dump((maxlen, word_list, used_letter_combos), f)
    sys.stderr.write("Done!\n")
    sys.stderr.flush()
    with open(pkl, "rb") as f:
        return pickle.load(f)


#
# Directions
#    3 2 1
#    4 X 0
#    5 6 7
#
moves = [
    np.array(( 0,  1)), # 0
    np.array((-1,  1)), # 1
    np.array((-1,  0)), # 2
    np.array((-1, -1)), # 3
    np.array(( 0, -1)), # 4
    np.array(( 1, -1)), # 5
    np.array(( 1,  0)), # 6
    np.array(( 1,  1))  # 7
]

def solve(board, position, word, dictionary, solutions, used_combos):
    x, y = position
    oldchar = board[x][y]
    board[x][y] = '-'
    word += oldchar
    n = len(word)
    if ((n >= 2 and word[-2:] not in used_combos) or
        (n >= 3 and word[-3:] not in used_combos) or
        (n >= 4 and word[-4:] not in used_combos) or
        (n >= 5 and word[-5:] not in used_combos) or
        (n >= 6 and word[-6:] not in used_combos)):
        board[x][y] = oldchar
        return
    if word in dictionary and word not in solutions and len(word) > 2:
        solutions.append(word)
    for move in moves:
        movex, movey = move[0], move[1]
        newx = x + movex
        newy = y + movey
        if (newx >= 4 or newx < 0 or
            newy >= 4 or newy < 0):
            # out of bounds
            continue
        if board[newx][newy] == '-':
            # already used
            continue
        solve(board, (newx, newy), word, dictionary, solutions, used_combos)
    board[x][y] = oldchar

def get_score(words):
    score = 0
    for word in words:
        n = len(word)
        if n==3 or n==4:
            score += 1
        elif n==5:
            score += 2
        elif n==6:
            score += 3
        elif n==7:
            score += 5
        else:
            score += 11
    return score


def get_args():
    p = argparse.ArgumentParser()
    # Add 'solve' and 'results' subcommands
    subparsers = p.add_subparsers(dest='command')
    solve_parser = subparsers.add_parser('solve')
    solve_parser.add_argument('-n', type=int, help='number of boards', default=100)
    results_parser = subparsers.add_parser('results')
    args = p.parse_args()
    if args.command is None:
        p.print_help()
        exit()
    return args

def solve_board(dictionary, used_combos, boards, all_solutions):
    board = get_board()
    solutions = []
    for x in range(4):
        for y in range(4):
            solve(board, (x, y), '', dictionary, solutions, used_combos)
    solutions = sorted(solutions)
    boards.append(board.tolist())
    all_solutions.append(solutions)


def solve_boards(count):
    maxlen, dictionary, used_combos = get_dictionary()
    boards = []
    all_solutions = []
    for i in  range(count):
        if i % 100 == 0:
            sys.stderr.write(f"Board {i}\n")
        solve_board(dictionary, used_combos, boards, all_solutions)

    with open("solutions.json", "w", encoding='utf-8') as f:
        r = []
        for board, solutions in zip(boards, all_solutions):
            r.append({'board': board, 'solutions': solutions, 'n': len(solutions)})
        json.dump(r, f)

def do_results(args):
    r = json.load(open("solutions.json"))
    boards = []
    for b in r:
        boards.append((len(b['solutions']), b['solutions'], b['board']))
    boards = sorted(boards, key=lambda x: x[0])
    print(boards[0])
    print(boards[1])
    print(boards[2])
    print(boards[-1])


def main():
    args = get_args()
    if args.command == 'solve':
        solve_boards(args.n)
    elif args.command == 'results':
        do_results(args)

if __name__ == '__main__':
    main()

