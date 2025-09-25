from typing import List, Tuple
import time
from local_driver import Alg3D, Board

class WinningPatterns:
    """76種類の勝利パターンを管理するクラス"""
    
    @staticmethod
    def generate_all_winning_lines():
        """76種類の勝利ラインを生成"""
        lines = []
        
        # 1. 水平線（x方向）: 16パターン (4面 × 4行)
        for z in range(4):
            for y in range(4):
                line = [(x, y, z) for x in range(4)]
                lines.append(line)
        
        # 2. 垂直線（y方向）: 16パターン (4面 × 4列)
        for z in range(4):
            for x in range(4):
                line = [(x, y, z) for y in range(4)]
                lines.append(line)
        
        # 3. 平面対角線: 8パターン (4面 × 2対角)
        for z in range(4):
            # 主対角線（左上→右下）
            line1 = [(i, i, z) for i in range(4)]
            lines.append(line1)
            # 副対角線（右上→左下）
            line2 = [(i, 3-i, z) for i in range(4)]
            lines.append(line2)
        
        # 4. z軸垂直: 16パターン (4×4位置)
        for x in range(4):
            for y in range(4):
                line = [(x, y, z) for z in range(4)]
                lines.append(line)
        
        # 5. 3D対角線: 20パターン
        
        # 5-1. 面対角（z軸+平面対角）: 16パターン
        # x-z平面の対角線 (y固定)
        for y in range(4):
            # 主対角線
            line1 = [(i, y, i) for i in range(4)]
            lines.append(line1)
            # 副対角線
            line2 = [(i, y, 3-i) for i in range(4)]
            lines.append(line2)
        
        # y-z平面の対角線 (x固定)
        for x in range(4):
            # 主対角線
            line1 = [(x, i, i) for i in range(4)]
            lines.append(line1)
            # 副対角線
            line2 = = [(x, i, 3-i) for i in range(4)]
            lines.append(line2)
        
        # 5-2. 空間対角線: 4パターン
        # 完全3D対角線
        space_diagonals = [
            [(i, i, i) for i in range(4)],           # (0,0,0)→(3,3,3)
            [(i, i, 3-i) for i in range(4)],         # (0,0,3)→(3,3,0)
            [(i, 3-i, i) for i in range(4)],         # (0,3,0)→(3,0,3)
            [(i, 3-i, 3-i) for i in range(4)]        # (0,3,3)→(3,0,0)
        ]
        lines.extend(space_diagonals)
        
        return lines

class OptimalAI(Alg3D):
    def __init__(self):
        # 位置価値マトリックス
        self.POSITION_VALUES = [
            [[1,2,2,1], [2,3,3,2], [2,3,3,2], [1,2,2,1]],  # z=0
            [[2,3,3,2], [3,4,4,3], [3,4,4,3], [2,3,3,2]],  # z=1
            [[2,3,3,2], [3,4,4,3], [3,4,4,3], [2,3,3,2]],  # z=2
            [[1,2,2,1], [2,3,3,2], [2,3,3,2], [1,2,2,1]]   # z=3
        ]
        
        # 勝利ライン（76パターン）
        self.winning_lines = WinningPatterns.generate_all_winning_lines()
        
        # 時間管理
        self.start_time = 0
        self.time_limit = 9.0
    
    def get_move(self, board: Board, player: int, last_move: Tuple[int, int, int]) -> Tuple[int, int]:
        self.start_time = time.time()
        
        # 1. 即座勝利チェック
        winning_move = self.find_winning_move(board, player)
        if winning_move:
            return winning_move
        
        # 2. 脅威ブロック
        opponent = 3 - player
        blocking_move = self.find_winning_move(board, opponent)
        if blocking_move:
            return blocking_move
        
        # 3. 中心優先戦略
        return self.get_center_move(board)
    
    def is_valid_move(self, board: Board, x: int, y: int) -> bool:
        if not (0 <= x <= 3 and 0 <= y <= 3):
            return False
        return board[3][y][x] == 0
    
    def make_move(self, board: Board, x: int, y: int, player: int) -> Board:
        new_board = [[[board[z][y][x] for x in range(4)] for y in range(4)] for z in range(4)]
        
        for z in range(4):
            if new_board[z][y][x] == 0:
                new_board[z][y][x] = player
                break
        
        return new_board
    
    def find_winning_move(self, board: Board, player: int) -> Tuple[int, int] or None:
        for x in range(4):
            for y in range(4):
                if self.is_valid_move(board, x, y):
                    test_board = self.make_move(board, x, y, player)
                    if self.is_winning_position(test_board, player):
                        return (x, y)
        return None
    
    def is_winning_position(self, board: Board, player: int) -> bool:
        """76パターン全ての勝利判定"""
        for line in self.winning_lines:
            if self.check_line(board, line, player):
                return True
        return False
    
    def check_line(self, board: Board, line: List[Tuple[int, int, int]], player: int) -> bool:
        """指定されたラインが4連続かチェック"""
        for x, y, z in line:
            if board[z][y][x] != player:
                return False
        return True
    
    def count_line_stones(self, board: Board, line: List[Tuple[int, int, int]], player: int) -> Tuple[int, int]:
        """ライン上の石の数をカウント（自分の石、相手の石）"""
        my_count = 0
        opponent_count = 0
        opponent = 3 - player
        
        for x, y, z in line:
            if board[z][y][x] == player:
                my_count += 1
            elif board[z][y][x] == opponent:
                opponent_count += 1
        
        return my_count, opponent_count
    
    def get_center_move(self, board: Board) -> Tuple[int, int]:
        priority_positions = [
            (1,1), (2,1), (1,2), (2,2),
            (0,1), (3,1), (1,0), (1,3), (2,0), (2,3), (0,2), (3,2),
            (0,0), (0,3), (3,0), (3,3)
        ]
        
        for x, y in priority_positions:
            if self.is_valid_move(board, x, y):
                return (x, y)
        
        return (0, 0)

class MyAI(OptimalAI):
    pass