#!/usr/bin/python3
"""
N-Queens backtracking program to print the coordinates of N queens
on an NxN grid such that they are all in non-attacking positions.
"""

from sys import argv

if __name__ == "__main__":
    board = []

    if len(argv) != 2:
        print("Usage: nqueens N")
        exit(1)

    if not argv[1].isdigit():
        print("N must be a number")
        exit(1)

    N = int(argv[1])

    if N < 4:
        print("N must be at least 4")
        exit(1)

    # Initialize the board as an empty NxN grid
    for i in range(N):
        board.append([i, None])

    def is_queen_already_placed(y):
        """Check if a queen already exists in the same column (y)."""
        for x in range(N):
            if y == board[x][1]:
                return True
        return False

    def is_attack(x, y):
        """Determine whether or not the placement leads to an attack."""
        if is_queen_already_placed(y):
            return False
        i = 0
        while i < x:
            if abs(board[i][1] - y) == abs(i - x):
                return False
            i += 1
        return True

    def clear_board_from_x(x):
        """Clears the board from the point of failure onwards."""
        for i in range(x, N):
            board[i][1] = None

    def solve_nqueens(x):
        """Recursive backtracking function to find the solution."""
        for y in range(N):
            clear_board_from_x(x)
            if is_attack(x, y):
                board[x][1] = y
                if x == N - 1:
                    print(board)
                else:
                    solve_nqueens(x + 1)

    # Start the recursive process at x = 0
    solve_nqueens(0)
