# boggle
import numpy as np
import sys
import sqlite3
import time
import string
import random
import copy
import pickle
from pathlib import Path
import json
import argparse
import matplotlib.pyplot as plt
from multiprocessing import Pool

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



def solve_board(dictionary, used_combos):
    board = get_board()
    solutions = []
    for x in range(4):
        for y in range(4):
            solve(board, (x, y), '', dictionary, solutions, used_combos)
    return board, solutions

def solve_boards(args):
    process_id, count = args
    maxlen, dictionary, used_combos = get_dictionary()
    boards = []
    all_solutions = []
    for i in  range(count):
        if i % 100 == 0:
            sys.stderr.write(f"Board {process_id} {i}\n")
        board, solution = solve_board(dictionary, used_combos)
        all_solutions.append((board.tolist(), solution))
    sys.stderr.write(f"Process {process_id} completed")
    return all_solutions

def str_board(board):
    result = "\n".join([''.join(line) for line in board])
    return result

def print_board(board):
    n, solutions, board = board
    for line in board:
        print(" ".join(line))
    print(f'found {n} solutions: [{", ".join(solutions)}]')

def load_results():
    solutions_base = "solutions"
    solutions_json = Path(f"{solutions_base}.json")
    solutions_pkl = Path(f"{solutions_base}.pkl")

    if (solutions_json.exists() and solutions_pkl.exists() and
        (solutions_pkl.stat().st_mtime > solutions_json.stat().st_mtime)):
        sys.stderr.write("Loading pickle..."); sys.stderr.flush()
        r = pickle.load(open(solutions_pkl, 'rb'))
    else:
        sys.stderr.write("Loading json..."); sys.stderr.flush()
        r = json.load(open(solutions_json))
        sys.stderr.write("Saving pickle..."); sys.stderr.flush()
        pickle.dump(r, open(solutions_pkl, 'wb'))
    sys.stderr.write("Done\n"); sys.stderr.flush()
    return r

def do_results(args):
    r = load_results()
    boards = []
    n_solutions = []
    for b in r:
        boards.append((len(b['solutions']), b['solutions'], b['board']))
        n_solutions.append(len(b['solutions']))
    boards = sorted(boards, key=lambda x: x[0])
    print_board(boards[0])
    print_board(boards[-1])
    nbins = np.max(n_solutions)
    width = np.max(n_solutions)/nbins
    histogram, bin_edges = np.histogram(n_solutions, bins=nbins)
    if args.log:
        histogram = np.log10(histogram)
    plt.bar(bin_edges[:-1], histogram, width=width, edgecolor='black')
    plt.xlabel("Number of words found on board")
    plt.ylabel("Frequency")
    plt.show()

def do_sqlite_results(args):
    fn = "test.db"
    path = Path(fn)
    cx = sqlite3.connect(path)
    sys.stderr.write("selecting all..."); sys.stderr.flush()
    r = cx.execute("select board, words from boards")
    boards = []
    n_solutions = []
    for board, n in r:
        n_solutions.append(n)
    sys.stderr.write("done\n"); sys.stderr.flush()

    r = cx.execute("select min(n_words) from boards")
    minwords = None
    maxwords = None
    for x in r:
        minwords = x[0]
        break

    r = cx.execute("select max(n_words) from boards")
    for x in r:
        maxwords = x[0]
        break

    print(maxwords, minwords)
    minboards = cx.execute("select id, board, n_words, words from boards where n_words == ?", (minwords, ))
    maxboards = cx.execute("select id, board, n_words, words from boards where n_words == ?", (maxwords, ))
    for x in maxboards:
        boardid, board, n_words, words = x
        print("****************************")
        print(board)
        print(words)
        print("----------------------------")

    for x in minboards:
        boardid, board, n_words, words = x
        print("****************************")
        print(board)
        if n_words > 0:
            print(words)
        print("----------------------------")
    exit()
    nbins = np.max(n_solutions)
    width = np.max(n_solutions)/nbins
    histogram, bin_edges = np.histogram(n_solutions, bins=nbins)
    if args.log:
        histogram = np.log10(histogram)
    plt.bar(bin_edges[:-1], histogram, width=width, edgecolor='black')
    plt.xlabel("Number of words found on board")
    plt.ylabel("Frequency")
    plt.show()

def dispatch_solve_boards(count, threads):
    n_per_process = int(count/threads+0.5)
    arg_list = [(i, n_per_process) for i in range(threads)]
    with Pool() as pool:
        results = pool.map(solve_boards, arg_list)
    
    boards = []
    solutions = []
    for result in results:
        for board, solution in result:
            boards.append(board)
            solutions.append(solution)
    
    with open("solutions.json", "w", encoding='utf-8') as f:
        r = []
        for board, solution in zip(boards, solutions):
            r.append({'board': board, 'solutions': solution, 'n': len(solution)})
        json.dump(r, f)


def do_json2sqlite(args):
    fn = "test.db"
    path = Path(fn)
    if path.exists():
        path.unlink()
    
    cx = sqlite3.connect(path)
    cx.execute("create table boards(id, board, n_words, words)")
    r = load_results()
    for i, x in enumerate(r):
        board = x['board']
        words = x['solutions']
        s_board = str_board(board)
        cx.execute("insert into boards values (?, ?, ?, ?)", (i, s_board, len(words), ",".join(words)))
        if (i%100) == 0:
            cx.commit()
    cx.commit()
    cx.close()
def main():
    args = get_args()
    if args.command == 'solve':
        dispatch_solve_boards(args.n, args.parallel)
    elif args.command == 'results':
        do_results(args)
    elif args.command == 'json2sqlite':
        do_json2sqlite(args)
    elif args.command == 'sqlite_results':
        do_sqlite_results(args)
    else:
        raise ValueError(f"unknown command {args.command}")

def get_args():
    p = argparse.ArgumentParser()
    # Add 'solve' and 'results' subcommands
    subparsers = p.add_subparsers(dest='command')
    solve_parser = subparsers.add_parser('solve')
    solve_parser.add_argument('-n', type=int, help='number of boards', default=100)
    solve_parser.add_argument('-j', '--parallel', type=int, help="number of parallel threads, default=8", default=8)
    results_parser = subparsers.add_parser('results')
    results_parser.add_argument('-l', '--log', action='store_true', help="Log plot")
    sqlite = subparsers.add_parser(name='json2sqlite')
    sqlite_results = subparsers.add_parser(name='sqlite_results')
    sqlite_results.add_argument('-l', '--log', action='store_true', help="Log plot")
    args = p.parse_args()
    if args.command is None:
        p.print_help()
        exit()
    return args
if __name__ == '__main__':
    main()

