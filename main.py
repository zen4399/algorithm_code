from typing import List, Tuple
from local_driver import Alg3D, Board # ローカル検証用
import math
import copy
#from framework import Alg3D, Board # 本番用


class MyAI(Alg3D):
    def get_move(
        self,
        board: List[List[List[int]]], # 盤面情報
        player: int, # 先手(黒):1 後手(白):2
        last_move: Tuple[int, int, int] # 直前に置かれた場所(x, y, z)
    ) -> Tuple[int, int]: # 置く場所(x, y)
        # ここにアルゴリズムを書く
        _, move = alphabeta(board, depth=3, alpha=-math.inf, beta=math.inf, maximizing=True, player=player)
        return move

# ビットボード変換ヘルパー
def board_to_bitboards(board: List[List[List[int]]]):
    p1 = 0
    p2 = 0
    for z in range(4):
        for y in range(4):
            for x in range(4):
                idx = z*16 + y*4 + x
                if board[z][y][x] == 1:
                    p1 |= 1 << idx
                elif board[z][y][x] == 2:
                    p2 |= 1 << idx
    return p1, p2

# 勝利判定
def is_win(bitboard: int) -> bool:
    # 簡略化: x, y, z軸と主要対角のみ（必要なら全13方向追加）
    lines = []

    # x方向
    for z in range(4):
        for y in range(4):
            mask = 0
            for x in range(4):
                mask |= 1 << (z*16 + y*4 + x)
            lines.append(mask)
    # y方向
    for z in range(4):
        for x in range(4):
            mask = 0
            for y in range(4):
                mask |= 1 << (z*16 + y*4 + x)
            lines.append(mask)
    # z方向
    for y in range(4):
        for x in range(4):
            mask = 0
            for z in range(4):
                mask |= 1 << (z*16 + y*4 + x)
            lines.append(mask)

    for mask in lines:
        if (bitboard & mask) == mask:
            return True
    return False

# 有効手列挙
def valid_moves(board: List[List[List[int]]]) -> List[Tuple[int,int]]:
    moves = []
    for x in range(4):
        for y in range(4):
            if board[3][y][x] == 0:
                moves.append((x, y))
    print(moves)
    return moves

# 評価関数（簡易: 3連を狙う）
def evaluate(board: List[List[List[int]]], player: int) -> int:
    # 勝ち判定最優先
    p1, p2 = board_to_bitboards(board)
    if is_win(p1):
        return 1000 if player == 1 else -1000
    if is_win(p2):
        return 1000 if player == 2 else -1000
    return 0  # ここを拡張して3連/2連加点可能

# αβ探索
def alphabeta(board: List[List[List[int]]], depth: int, alpha: int, beta: int, maximizing: bool, player: int):
    moves = valid_moves(board)
    if depth == 0 or not moves:
        return evaluate(board, player), None

    best_move = moves[0]
    if maximizing:
        max_eval = -math.inf
        for x, y in moves:
            # 置く
            new_board = copy.deepcopy(board)
            for z in range(4):
                if new_board[z][y][x] == 0:
                    new_board[z][y][x] = player
                    break
            eval_score, _ = alphabeta(new_board, depth-1, alpha, beta, False, player)
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = (x, y)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        opp = 3 - player
        for x, y in moves:
            new_board = copy.deepcopy(board)
            for z in range(4):
                if new_board[z][y][x] == 0:
                    new_board[z][y][x] = opp
                    break
            eval_score, _ = alphabeta(new_board, depth-1, alpha, beta, True, player)
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = (x, y)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move
