import secrets
from functools import partial
from pathlib import Path

import numpy as np
from nicegui import elements, events, ui


class Game:
    """ナンバープレースゲーム"""

    board_num: np.ndarray  # 盤面の数字
    board_fix: np.ndarray  # 数字が固定かどうか
    board_err: np.ndarray  # エラーかどうか
    labels: list[list[elements.label]]  # 9x9のマス
    message = ""  # 判定メッセージ
    select = 0  # 選択
    select_buttons: list[elements.button]  # 選択用ボタン

    def __init__(self):
        self.board_num = np.zeros((9, 9), dtype=np.int8)
        self.board_fix = np.zeros((9, 9), dtype=bool)
        self.board_err = np.zeros((9, 9), dtype=bool)
        ui.label().bind_text(self, "message").classes("text-3xl")
        classes = "w-12 h-12 leading-normal text-3xl text-center border border-black cursor-default"
        with ui.row().style("user-select: none;"):
            with ui.grid(columns=9).classes("gap-0"):
                self.labels = []
                for x in range(9):
                    lines = []
                    for y in range(9):
                        click = partial(self.click, x, y)
                        ex = " bg-gray-100" if (x // 3 + y // 3) % 2 else ""
                        lines.append(ui.label().classes(classes + ex).on("click", click))
                    self.labels.append(lines)
            with ui.column().classes("gap-3"):
                with ui.grid(columns=3).classes("gap-1"):
                    self.select_buttons = [
                        ui.button(str(i)).classes("w-12 h-12 text-xl bg-gray-100") for i in range(1, 10)
                    ]
                self.select_buttons.insert(0, ui.button("erase").classes("w-full bg-gray-100"))
                for button in self.select_buttons:
                    button.props("flat").on_click(self.select_click)
                ui.button("clear", on_click=self.clear).classes("w-full")
                ui.upload(on_upload=self.upload).props("accept=.txt").classes("w-full")
        with ui.row():
            ui.button("new_game", on_click=self.new_game)
            ui.button("download", on_click=lambda: ui.download(self.to_bytes(), "data.txt"))
        self.new_game()

    def new_game(self, data: bytes | None = None) -> None:
        """新規ゲーム"""
        self.select = 0
        if not data:
            probs = [*(Path(__file__).parent / "problem").glob("data*.txt")]
            data = secrets.choice(probs).read_bytes()
        self.from_bytes(data)

    def rebuild(self) -> None:
        """GUIの再作成"""
        self.message = self.judge()
        for x in range(9):
            for y in range(9):
                value = self.board_num[x, y]
                label = self.labels[x][y]
                label.text = str(value) if value else ""
                if not value:
                    continue
                if self.board_fix[x, y]:
                    label.classes("font-bold", remove="cursor-pointer")
                else:
                    label.classes("cursor-pointer", remove="font-bold")
                label.classes(remove="text-red text-blue")
                if self.board_err[x, y]:
                    label.classes("text-red", remove="text-blue")
                elif self.board_num[x, y] == self.select:
                    label.classes("text-blue", remove="text-red")
        # 選択ボタンの色
        for i in range(10):
            button = self.select_buttons[i]
            button.classes(remove="bg-green-500 bg-green-300")
            if i and (self.board_num == i).sum() >= 9:  # noqa: PLR2004
                button.classes("bg-green-500")
            elif i == self.select:
                button.classes("bg-green-300")

    def judge(self) -> str:
        """終局判定"""
        self.board_err[:] = False
        for num in range(1, 10):
            for i in range(9):
                target = self.board_num[i] == num
                if target.sum() > 1:
                    self.board_err[i][target] = True
                target = self.board_num[:, i] == num
                if target.sum() > 1:
                    self.board_err[:, i][target] = True
            for sx in range(0, 9, 3):
                for sy in range(0, 9, 3):
                    target = self.board_num[sx : sx + 3, sy : sy + 3] == num
                    if target.sum() > 1:
                        self.board_err[sx : sx + 3, sy : sy + 3][target] = True
        if remain := (self.board_num == 0).sum():
            return f"残り {remain}"
        return "不正解!" if self.board_err.any() else "クリア!"

    def clear(self) -> None:
        """固定以外を消去"""
        self.board_num[:] = self.board_num * self.board_fix
        self.rebuild()

    def click(self, x: int, y: int) -> None:
        """マスのクリック"""
        if not self.board_fix[x, y]:
            self.board_num[x, y] = 0 if self.board_num[x, y] == self.select else self.select
            self.rebuild()

    def select_click(self, event) -> None:
        """選択のクリック"""
        text = event.sender.text
        self.select = 0 if text == "erase" else int(text)
        self.rebuild()

    def to_bytes(self) -> bytes:
        """盤面をバイト文字列化"""
        return "\n".join("".join(line) for line in self.board_num.astype(str)).encode(encoding="utf-8")

    def from_bytes(self, data: bytes) -> None:
        """バイト文字列から盤面を復元"""
        bs = data.decode(encoding="utf-8").replace("\n", "")
        self.board_num[:] = np.array([*bs], dtype=np.int8).reshape((9, 9))
        self.board_fix[:] = self.board_num != 0
        self.rebuild()

    def upload(self, ev: events.UploadEventArguments) -> None:
        """ファイルから盤面を読込(数字は固定とみなす)"""
        self.from_bytes(ev.content.read())


def main(*, reload=False, port=8103):
    Game()
    ui.run(title="Number Place", reload=reload, port=port)
