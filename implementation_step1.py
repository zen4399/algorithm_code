from typing import List, Tuple
import time
from local_driver import Alg3D, Board

class OptimalAI(Alg3D):
    def __init__(self):
        # 位置価値マトリックス（中心ほど高価値）
        self.POSITION_VALUES = [
            [[1,2,2,1], [2,3,3,2], [2,3,3,2], [1,2,2,1]],  # z=0
            [[2,3,3,2], [3,4,4,3], [3,4,4,3], [2,3,3,2]],  # z=1
            [[2,3,3,2], [3,4,4,3], [3,4,4,3], [2,3,3,2]],  # z=2
            [[1,2,2,1], [2,3,3,2], [2,3,3,2], [1,2,2,1]]   # z=3
        ]
        
        # 時間管理用
        self.start_time = 0
        self.time_limit = 9.0  # 9秒に設定（余裕を持たせる）
    
    def get_move(self, board: Board, player: int, last_move: Tuple[int, int, int]) -> Tuple[int, int]:
        self.start_time = time.time()
        
        # 1. 即座勝利チェック
        winning_move = self.find_winning_move(board, player)
        if winning_move:
            return winning_move
        
        # 2. 脅威ブロックチェック
        opponent = 3 - player  # 1→2, 2→1
        blocking_move = self.find_winning_move(board, opponent)
        if blocking_move:
            return blocking_move
        
        # 3. 中心優先の単純戦略（暫定）
        return self.get_center_move(board)
    
    def is_valid_move(self, board: Board, x: int, y: int) -> bool:
        """指定位置に石を置けるかチェック"""
        if not (0 <= x <= 3 and 0 <= y <= 3):
            return False
        return board[3][y][x] == 0  # 最上層が空いているか
    
    def get_valid_moves(self, board: Board) -> List[Tuple[int, int]]:
        """有効な手のリストを取得"""
        moves = []
        for y in range(4):
            for x in range(4):
                if self.is_valid_move(board, x, y):
                    moves.append((x, y))
        return moves
    
    def make_move(self, board: Board, x: int, y: int, player: int) -> Board:
        """盤面に石を配置（重力適用）して新しい盤面を返す"""
        new_board = [[[board[z][y][x] for x in range(4)] for y in range(4)] for z in range(4)]
        
        # 重力で下から石を配置
        for z in range(4):
            if new_board[z][y][x] == 0:
                new_board[z][y][x] = player
                break
        
        return new_board
    
    def find_winning_move(self, board: Board, player: int) -> Tuple[int, int] or None:
        """1手で勝利できる手を探す"""
        for x in range(4):
            for y in range(4):
                if self.is_valid_move(board, x, y):
                    test_board = self.make_move(board, x, y, player)
                    if self.is_winning_position(test_board, player):
                        return (x, y)
        return None
    
    def get_center_move(self, board: Board) -> Tuple[int, int]:
        """中心優先の手を選択"""
        # 中心から外側への優先順位
        priority_positions = [
            (1,1), (2,1), (1,2), (2,2),  # 中心4マス
            (0,1), (3,1), (1,0), (1,3), (2,0), (2,3), (0,2), (3,2),  # 中心周辺
            (0,0), (0,3), (3,0), (3,3)   # 隅
        ]
        
        for x, y in priority_positions:
            if self.is_valid_move(board, x, y):
                return (x, y)
        
        # フォールバック
        return (0, 0)
    
    def is_winning_position(self, board: Board, player: int) -> bool:
        """勝利判定（暫定：簡単なパターンのみ）"""
        # TODO: Step 2で76パターン全て実装
        
        # 水平線チェック（各z平面のx方向）
        for z in range(4):
            for y in range(4):
                count = 0
                for x in range(4):
                    if board[z][y][x] == player:
                        count += 1
                    else:
                        count = 0
                    if count >= 4:
                        return True
        
        # 垂直線チェック（各z平面のy方向）
        for z in range(4):
            for x in range(4):
                count = 0
                for y in range(4):
                    if board[z][y][x] == player:
                        count += 1
                    else:
                        count = 0
                    if count >= 4:
                        return True
        
        return False
    
    def is_time_up(self) -> bool:
        """制限時間チェック"""
        return time.time() - self.start_time > self.time_limit

# MyAIクラス（提出用）
class MyAI(OptimalAI):
    pass