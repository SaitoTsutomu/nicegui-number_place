# flake8: noqa: S101
from nicegui_number_place import Game


def test_game():
    """ゲームのテスト"""
    game = Game()
    data = b"502173869698542137371896524469328751827415693135769248284951376753684912916237485"
    game.from_bytes(data)
    game.select = 1
    game.click(0, 1)
    assert game.message == "不正解!"
    game.click(0, 1)
    game.select = 4
    game.click(0, 1)
    assert game.message == "クリア!"
