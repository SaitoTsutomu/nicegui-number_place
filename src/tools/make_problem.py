from pathlib import Path

import numpy as np
from mip import Model, maximize, xsum


def solve(board: np.ndarray, prize: np.ndarray, *, check_only_one=False) -> tuple[bool, np.ndarray]:
    """求解

    :param board: 固定値
    :param prize: 賞金
    :param checkOnlyOne: 解が1つか確認するか, defaults to False
    :return: 解があるかと問題
    """
    m = Model()
    v = m.add_var_tensor((9, 9, 9), "v", var_type="B")
    m.objective = maximize(xsum((prize * v).flat))
    m += v.sum(axis=0) == 1  # 1列に数字は1つ
    m += v.sum(axis=1) == 1  # 1行に数字は1つ
    m += v.sum(axis=2) == 1  # 1マスに数字は1つ
    for num in range(9):
        for sy in range(0, 9, 3):
            for sx in range(0, 9, 3):
                m += xsum(v[sy : sy + 3, sx : sx + 3, num].flat) == 1  # 3x3に数字は1つ
        m += v[board == num + 1, num] == 1  # 固定
    m.verbose = 0
    m.optimize()
    solved = m.status.value == 0
    value = v.astype(float, subok=False).round().astype(int)
    if solved and check_only_one:
        m += xsum(v[value == 1]) <= 81 - 1
        solved = m.optimize().value != 0
    return solved, (value * range(1, 10)).sum(axis=2)


def make_problem(seed: int | None = None, reduce: int = 20) -> np.ndarray:
    """問題を作成

    :param seed: 乱数シード, defaults to None
    :param reduce: 削減数, defaults to 20
    :return: 問題
    """
    rng = np.random.default_rng(seed)
    prize = rng.random((9, 9))
    solved, board = solve(np.zeros((9, 9), dtype=np.int8), prize)
    while solved:
        arg = prize.argmax()
        y, x = arg // 9, arg % 9
        prize[y, x] = 0
        pre = board[y, x]
        board[y, x] = 0
        solved, _ = solve(board, prize, check_only_one=True)
    board[y, x] = pre
    for _ in range(reduce):
        for _ in range(99):
            y, x = rng.integers(0, 9, 2)
            if board[y, x]:
                break
        if not board[y, x]:
            break
        pre = board[y, x]
        board[y, x] = 0
        if not solve(board, prize, check_only_one=True)[0]:
            board[y, x] = pre
    return board


if __name__ == "__main__":
    pth = Path("problem")
    pth.mkdir(exist_ok=True)
    for i in range(1000):
        board = make_problem()
        s = "\n".join("".join(line) for line in board.astype(str))
        (pth / f"data{i:03}.txt").write_text(s)
