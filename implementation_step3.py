from typing import List, Tuple
import time
from local_driver import Alg3D, Board

class WinningPatterns:
    @staticmethod
    def generate_all_winning_lines():
        lines = []
        
        # 1. 水平線（x方向）: 16パターン
        for z in range(4):
            for y in range(4):
                line = [(x, y, z) for x in range(4)]
                lines.append(line)
        
        # 2. 垂直線（y方向）: 16パターン
        for z in range(4):
            for x in range(4):
                line = [(x, y, z) for y in range(4)]
                lines.append(line)
        
        # 3. 平面対角線: 8パターン
        for z in range(4):
            line1 = [(i, i, z) for i in range(4)]
            lines.append(line1)
            line2 = [(i, 3-i, z) for i in range(4)]
            lines.append(line2)
        
        # 4. z軸垂直: 16パターン
        for x in range(4):
            for y in range(4):
                line = [(x, y, z) for z in range(4)]
                lines.append(line)
        
        # 5. 3D対角線: 20パターン
        # x-z平面の対角線
        for y in range(4):
            line1 = [(i, y, i) for i in range(4)]
            lines.append(line1)
            line2 = [(i, y, 3-i) for i in range(4)]
            lines.append(line2)
        
        # y-z平面の対角線
        for x in range(4):
            line1 = [(x, i, i) for i in range(4)]
            lines.append(line1)
            line2 = [(x, i, 3-i) for i in range(4)]
            lines.append(line2)
        
        # 空間対角線: 4パターン
        space_diagonals = [
            [(i, i, i) for i in range(4)],
            [(i, i, 3-i) for i in range(4)],
            [(i, 3-i, i) for i in range(4)],
            [(i, 3-i, 3-i) for i in range(4)]
        ]
        lines.extend(space_diagonals)
        
        return lines

class PositionEvaluator:
    """位置評価を行うクラス"""
    
    def __init__(self):
        # 位置価値マトリックス（中心ほど高価値）
        self.POSITION_VALUES = [
            [[1,2,2,1], [2,3,3,2], [2,3,3,2], [1,2,2,1]],  # z=0
            [[2,3,3,2], [3,4,4,3], [3,4,4,3], [2,3,3,2]],  # z=1
            [[2,3,3,2], [3,4,4,3], [3,4,4,3], [2,3,3,2]],  # z=2
            [[1,2,2,1], [2,3,3,2], [2,3,3,2], [1,2,2,1]]   # z=3
        ]
        
        self.winning_lines = WinningPatterns.generate_all_winning_lines()
    
    def evaluate_position(self, board: Board, player: int) -> int:
        """総合的な位置評価"""
        score = 0
        
        # 1. 勝利ライン評価
        score += self.evaluate_winning_lines(board, player)
        
        # 2. 中心制御評価
        score += self.evaluate_center_control(board, player)
        
        # 3. 高度優位性評価
        score += self.evaluate_height_advantage(board, player)
        
        # 4. 脅威ブロッキング評価
        score += self.evaluate_threat_blocking(board, player)
        
        return score
    
    def evaluate_winning_lines(self, board: Board, player: int) -> int:
        """勝利ライン評価"""
        score = 0
        opponent = 3 - player
        
        for line in self.winning_lines:
            my_count, opponent_count = self.count_line_stones(board, line, player)
            
            # 相手の石があるラインは評価しない
            if opponent_count > 0:
                # 相手の脅威を評価
                if opponent_count == 2 and my_count == 0:
                    score -= 50  # 相手の2石連続を警戒
                elif opponent_count == 3 and my_count == 0:
                    score -= 500  # 相手の3石連続は危険
                continue
            
            # 自分の石のみのライン評価
            if my_count == 1:
                score += 1
            elif my_count == 2:
                score += 10  # 2石連続
            elif my_count == 3:
                score += 100  # 3石連続（勝利直前）
            elif my_count == 4:
                score += 1000  # 勝利
        
        return score
    
    def evaluate_center_control(self, board: Board, player: int) -> int:
        """中心制御の評価"""
        score = 0
        
        for z in range(4):
            for y in range(4):
                for x in range(4):
                    if board[z][y][x] == player:
                        score += self.POSITION_VALUES[z][y][x]
                    elif board[z][y][x] == (3 - player):
                        score -= self.POSITION_VALUES[z][y][x]
        
        return score
    
    def evaluate_height_advantage(self, board: Board, player: int) -> int:
        """高さの優位性評価"""
        score = 0
        
        for y in range(4):
            for x in range(4):
                # 各列での最上位の石を確認
                for z in range(3, -1, -1):
                    if board[z][y][x] != 0:
                        if board[z][y][x] == player:
                            score += z + 1  # 高い位置ほど有利
                        break
        
        return score
    
    def evaluate_threat_blocking(self, board: Board, player: int) -> int:
        """脅威ブロッキング評価"""
        score = 0
        opponent = 3 - player
        
        # 相手の勝利可能手をカウント
        opponent_winning_moves = 0
        for x in range(4):
            for y in range(4):
                if self.is_valid_move(board, x, y):
                    test_board = self.make_move(board, x, y, opponent)
                    if self.is_winning_position(test_board, opponent):
                        opponent_winning_moves += 1
        
        # 相手の勝利可能手が多いほどマイナス
        score -= opponent_winning_moves * 100
        
        return score
    
    def count_line_stones(self, board: Board, line: List[Tuple[int, int, int]], player: int) -> Tuple[int, int]:
        my_count = 0
        opponent_count = 0
        opponent = 3 - player
        
        for x, y, z in line:
            if board[z][y][x] == player:
                my_count += 1
            elif board[z][y][x] == opponent:
                opponent_count += 1
        
        return my_count, opponent_count
    
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
    
    def is_winning_position(self, board: Board, player: int) -> bool:
        for line in self.winning_lines:
            if self.check_line(board, line, player):
                return True
        return False
    
    def check_line(self, board: Board, line: List[Tuple[int, int, int]], player: int) -> bool:
        for x, y, z in line:
            if board[z][y][x] != player:
                return False
        return True

class OptimalAI(Alg3D):
    def __init__(self):
        self.evaluator = PositionEvaluator()
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
        
        # 3. 評価関数による最適手選択
        return self.get_best_move_by_evaluation(board, player)
    
    def find_winning_move(self, board: Board, player: int) -> Tuple[int, int] or None:
        for x in range(4):
            for y in range(4):
                if self.evaluator.is_valid_move(board, x, y):
                    test_board = self.evaluator.make_move(board, x, y, player)
                    if self.evaluator.is_winning_position(test_board, player):
                        return (x, y)
        return None
    
    def get_best_move_by_evaluation(self, board: Board, player: int) -> Tuple[int, int]:
        """評価関数による最適手選択"""
        best_move = None
        best_score = float('-inf')
        
        valid_moves = self.get_valid_moves(board)
        
        for x, y in valid_moves:
            test_board = self.evaluator.make_move(board, x, y, player)
            score = self.evaluator.evaluate_position(test_board, player)
            
            if score > best_score:
                best_score = score
                best_move = (x, y)
        
        return best_move if best_move else (1, 1)  # フォールバック
    
    def get_valid_moves(self, board: Board) -> List[Tuple[int, int]]:
        moves = []
        for y in range(4):
            for x in range(4):
                if self.evaluator.is_valid_move(board, x, y):
                    moves.append((x, y))
        return moves

class MyAI(OptimalAI):
    pass