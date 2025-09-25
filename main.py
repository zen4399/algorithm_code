from typing import List, Tuple
from local_driver import Alg3D, Board # ローカル検証用
#from framework import Alg3D, Board # 本番用

class MyAI(Alg3D):
    def get_move(
        self,
        board: List[List[List[int]]], # 盤面情報
        player: int, # 先手(黒):1 後手(白):2
        last_move: Tuple[int, int, int] # 直前に置かれた場所(x, y, z)
    ) -> Tuple[int, int]:
        # ここにアルゴリズムを書く
        for y in range(4):
            for x in range(4):
                # 一番上(=z=3)まで埋まっていなければ置ける
                if board[3][y][x] == 0:
                    return (x, y)
        return (0, 0)