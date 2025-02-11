"""`number-place`実行"""

# ruff: noqa: T201
from pathlib import Path

import numpy as np
from make_problem import solve

if __name__ == "__main__":
    file = Path("src/nicegui_number_place/problem/data000.txt")
    s = file.read_text().replace("\n", "")
    board = np.array([*s], dtype=np.int8).reshape((9, 9))
    solved, _ = solve(board, np.zeros((9, 9)), check_only_one=True)
    print(board)
    print(solved)
