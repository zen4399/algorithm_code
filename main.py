from typing import List, Tuple, Optional
import time
#from local_driver import Alg3D, Board # ローカル検証用
from framework import Alg3D, Board # 本番用

class WinningPatterns:
    @staticmethod
    def generate_all_winning_lines():
        lines = []
        
        # 水平線（x方向）: 16パターン
        for z in range(4):
            for y in range(4):
                line = [(x, y, z) for x in range(4)]
                lines.append(line)
        
        # 垂直線（y方向）: 16パターン
        for z in range(4):
            for x in range(4):
                line = [(x, y, z) for y in range(4)]
                lines.append(line)
        
        # 平面対角線: 8パターン
        for z in range(4):
            line1 = [(i, i, z) for i in range(4)]
            lines.append(line1)
            line2 = [(i, 3-i, z) for i in range(4)]
            lines.append(line2)
        
        # z軸垂直: 16パターン
        for x in range(4):
            for y in range(4):
                line = [(x, y, z) for z in range(4)]
                lines.append(line)
        
        # 3D対角線: 20パターン
        for y in range(4):
            line1 = [(i, y, i) for i in range(4)]
            lines.append(line1)
            line2 = [(i, y, 3-i) for i in range(4)]
            lines.append(line2)
        
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

class TranspositionTable:
    def __init__(self, size=100000):
        self.table = {}
        self.max_size = size
    
    def get_board_hash(self, board: Board) -> str:
        return str(board)
    
    def store(self, board: Board, depth: int, score: int, flag: str, best_move: Optional[Tuple[int, int]]):
        board_hash = self.get_board_hash(board)
        if len(self.table) < self.max_size:
            self.table[board_hash] = (depth, score, flag, best_move)
    
    def lookup(self, board: Board, depth: int) -> Optional[Tuple[int, str, Optional[Tuple[int, int]]]]:
        board_hash = self.get_board_hash(board)
        if board_hash in self.table:
            stored_depth, score, flag, best_move = self.table[board_hash]
            if stored_depth >= depth:
                return score, flag, best_move
        return None

class GameEngine:
    def __init__(self):
        self.winning_lines = WinningPatterns.generate_all_winning_lines()
        self.POSITION_VALUES = [
            [[1,2,2,1], [2,3,3,2], [2,3,3,2], [1,2,2,1]],
            [[2,3,3,2], [3,4,4,3], [3,4,4,3], [2,3,3,2]],
            [[2,3,3,2], [3,4,4,3], [3,4,4,3], [2,3,3,2]],
            [[1,2,2,1], [2,3,3,2], [2,3,3,2], [1,2,2,1]]
        ]
    
    def is_valid_move(self, board: Board, x: int, y: int) -> bool:
        if not (0 <= x <= 3 and 0 <= y <= 3):
            return False
        return board[3][y][x] == 0
    
    def get_valid_moves(self, board: Board) -> List[Tuple[int, int]]:
        moves = []
        priority_positions = [
            (1,1), (2,1), (1,2), (2,2),
            (0,1), (3,1), (1,0), (1,3), (2,0), (2,3), (0,2), (3,2),
            (0,0), (0,3), (3,0), (3,3)
        ]
        
        for x, y in priority_positions:
            if self.is_valid_move(board, x, y):
                moves.append((x, y))
        
        return moves
    
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
    
    def is_board_full(self, board: Board) -> bool:
        for y in range(4):
            for x in range(4):
                if board[3][y][x] == 0:
                    return False
        return True
    
    def evaluate_position(self, board: Board, player: int) -> int:
        score = 0
        opponent = 3 - player
        
        if self.is_winning_position(board, player):
            return 10000
        if self.is_winning_position(board, opponent):
            return -10000
        if self.is_board_full(board):
            return 0
        
        # 勝利ライン評価
        for line in self.winning_lines:
            my_count, opponent_count = self.count_line_stones(board, line, player)
            
            if opponent_count > 0:
                if opponent_count == 2 and my_count == 0:
                    score -= 50
                elif opponent_count == 3 and my_count == 0:
                    score -= 500
                continue
            
            if my_count == 1:
                score += 1
            elif my_count == 2:
                score += 10
            elif my_count == 3:
                score += 100
        
        # 中心制御評価
        for z in range(4):
            for y in range(4):
                for x in range(4):
                    if board[z][y][x] == player:
                        score += self.POSITION_VALUES[z][y][x]
                    elif board[z][y][x] == opponent:
                        score -= self.POSITION_VALUES[z][y][x]
        
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

class MyAI(Alg3D):
    def __init__(self):
        self.game_engine = GameEngine()
        self.transposition_table = TranspositionTable()
        self.start_time = 0
        self.time_limit = 8.5
    
    def get_move(
        self,
        board: List[List[List[int]]],
        player: int,
        last_move: Tuple[int, int, int]
    ) -> Tuple[int, int]:
        self.start_time = time.time()
        
        # 即座勝利チェック
        winning_move = self.find_immediate_win(board, player)
        if winning_move:
            return winning_move
        
        # 脅威ブロック
        opponent = 3 - player
        blocking_move = self.find_immediate_win(board, opponent)
        if blocking_move:
            return blocking_move
        
        # Iterative Deepening Minimax
        best_move = None
        for depth in range(1, 8):
            if self.is_time_up():
                break
            
            move, score = self.minimax_with_alpha_beta(board, depth, float('-inf'), float('inf'), True, player)
            if move:
                best_move = move
        
        return best_move if best_move else (1, 1)
    
    def find_immediate_win(self, board: Board, player: int) -> Optional[Tuple[int, int]]:
        for x in range(4):
            for y in range(4):
                if self.game_engine.is_valid_move(board, x, y):
                    test_board = self.game_engine.make_move(board, x, y, player)
                    if self.game_engine.is_winning_position(test_board, player):
                        return (x, y)
        return None
    
    def minimax_with_alpha_beta(self, board: Board, depth: int, alpha: float, beta: float, 
                               maximizing_player: bool, original_player: int) -> Tuple[Optional[Tuple[int, int]], int]:
        
        if self.is_time_up():
            return None, self.game_engine.evaluate_position(board, original_player)
        
        # Transposition Table lookup
        tt_result = self.transposition_table.lookup(board, depth)
        if tt_result:
            score, flag, best_move = tt_result
            if flag == 'EXACT':
                return best_move, score
            elif flag == 'LOWERBOUND' and score >= beta:
                return best_move, score
            elif flag == 'UPPERBOUND' and score <= alpha:
                return best_move, score
        
        if depth == 0 or self.game_engine.is_board_full(board):
            score = self.game_engine.evaluate_position(board, original_player)
            return None, score
        
        current_player = original_player if maximizing_player else (3 - original_player)
        
        if self.game_engine.is_winning_position(board, current_player):
            score = 10000 - (10 - depth)
            return None, score if maximizing_player else -score
        
        valid_moves = self.game_engine.get_valid_moves(board)
        best_move = None
        original_alpha = alpha
        
        if maximizing_player:
            max_eval = float('-inf')
            for x, y in valid_moves:
                new_board = self.game_engine.make_move(board, x, y, current_player)
                _, eval_score = self.minimax_with_alpha_beta(new_board, depth - 1, alpha, beta, False, original_player)
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = (x, y)
                
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            
            # Transposition Table store
            flag = 'EXACT'
            if max_eval <= original_alpha:
                flag = 'UPPERBOUND'
            elif max_eval >= beta:
                flag = 'LOWERBOUND'
            
            self.transposition_table.store(board, depth, max_eval, flag, best_move)
            return best_move, max_eval
        else:
            min_eval = float('inf')
            for x, y in valid_moves:
                new_board = self.game_engine.make_move(board, x, y, current_player)
                _, eval_score = self.minimax_with_alpha_beta(new_board, depth - 1, alpha, beta, True, original_player)
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = (x, y)
                
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            
            # Transposition Table store
            flag = 'EXACT'
            if min_eval <= original_alpha:
                flag = 'UPPERBOUND'
            elif min_eval >= beta:
                flag = 'LOWERBOUND'
            
            self.transposition_table.store(board, depth, min_eval, flag, best_move)
            return best_move, min_eval
    
    def is_time_up(self) -> bool:
        return time.time() - self.start_time > self.time_limit