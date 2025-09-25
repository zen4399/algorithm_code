# 4×4×4立体四目並べ 最適アルゴリズム要件定義書

## 1. ゲーム仕様

### 1.1 基本ルール
- **盤面**: 4×4×4の立体格子（64マス）
- **プレイヤー**: 2人（先手：黒石=1、後手：白石=2）
- **重力**: 石は各列の最下層から積み重なる
- **座標系**: (x, y, z) ここで x,y ∈ [0,3], z ∈ [0,3]（z=0が最下層）

### 1.2 勝利条件（4石連続配置）

#### 1.2.1 基本的な4方向連続
1. **水平線**: 同一z平面内での横方向(x軸)連続
2. **垂直線**: 同一z平面内での縦方向(y軸)連続  
3. **対角線**: 同一z平面内での対角方向連続
4. **垂直積み**: 同一(x,y)位置でのz軸方向連続

#### 1.2.2 立体対角線（3D特有）
5. **面対角**: z軸方向と平面対角の組み合わせ（4種類）
6. **空間対角**: 3次元空間での完全対角線（4種類）

#### 1.2.3 勝利パターン総数
- **合計76の勝利ライン**
  - 水平線: 16パターン (4面 × 4行)
  - 垂直線: 16パターン (4面 × 4列)  
  - 平面対角線: 8パターン (4面 × 2対角)
  - z軸垂直: 16パターン (4×4位置)
  - 3D対角線: 20パターン (面対角16 + 空間対角4)

## 2. システム制約

### 2.1 実行制約
- **制限時間**: 1手あたり10秒
- **メモリ制限**: 約1GB
- **CPU時間**: 約3秒
- **Python バージョン**: 3.9互換

### 2.2 技術制約
- **使用可能**: Python標準ライブラリのみ
- **禁止**: ネットワーク、ファイルI/O、外部プロセス実行
- **必須インターフェース**: `get_move(board, player, last_move) -> (x, y)`

## 3. 最適アルゴリズム戦略

### 3.1 アルゴリズム分類

#### 3.1.1 Minimax系アルゴリズム
**推奨度: ★★★★★**

**基本Minimax + Alpha-Beta Pruning**
- **探索深度**: 6-8手先（制限時間内）
- **評価関数**: 位置価値 + 勝利ライン評価
- **枝刈り**: Alpha-Beta + Move ordering

**改良版**
- **Negamax**: 実装の簡素化
- **Iterative Deepening**: 時間制限対応
- **Transposition Table**: 重複計算回避

#### 3.1.2 Monte Carlo Tree Search (MCTS)
**推奨度: ★★★★☆**

- **UCB1選択**: 探索と活用のバランス
- **並列化**: マルチスレッド展開（制約内で）
- **ドメイン知識**: 勝利パターンの事前確率

#### 3.1.3 ハイブリッドアプローチ
**推奨度: ★★★★★**

- **序盤**: 定跡データベース
- **中盤**: Minimax with Alpha-Beta
- **終盤**: 完全探索（残り手数少ない場合）

### 3.2 評価関数設計

#### 3.2.1 基本評価要素
```python
def evaluate_position(board, player):
    score = 0
    
    # 1. 勝利ライン評価
    score += evaluate_winning_lines(board, player)
    
    # 2. 中心制御
    score += evaluate_center_control(board, player)
    
    # 3. 高度優位性
    score += evaluate_height_advantage(board, player)
    
    # 4. ブロッキング
    score += evaluate_threat_blocking(board, player)
    
    return score
```

#### 3.2.2 勝利ライン評価方式
- **2石連続**: +10点
- **3石連続**: +100点  
- **勝利直前**: +1000点
- **相手の脅威**: -50点（2石）, -500点（3石）

#### 3.2.3 位置価値マトリックス
```python
# 中心ほど高価値
POSITION_VALUES = [
    [[1,2,2,1], [2,3,3,2], [2,3,3,2], [1,2,2,1]],  # z=0
    [[2,3,3,2], [3,4,4,3], [3,4,4,3], [2,3,3,2]],  # z=1
    [[2,3,3,2], [3,4,4,3], [3,4,4,3], [2,3,3,2]],  # z=2
    [[1,2,2,1], [2,3,3,2], [2,3,3,2], [1,2,2,1]]   # z=3
]
```

### 3.3 最適化技術

#### 3.3.1 探索最適化
- **Move Ordering**: 中心→隅の順序
- **Killer Heuristic**: 過去の良手を優先
- **Null Move Pruning**: 手抜き探索による枝刈り

#### 3.3.2 メモ化戦略
```python
class TranspositionTable:
    def __init__(self, size=1000000):
        self.table = {}
        self.max_size = size
    
    def store(self, board_hash, depth, score, flag):
        if len(self.table) < self.max_size:
            self.table[board_hash] = (depth, score, flag)
```

#### 3.3.3 時間管理
```python
def time_management(remaining_time, moves_made):
    # 序盤: 多めの時間
    # 中盤: 標準時間  
    # 終盤: 精密計算
    if moves_made < 10:
        return remaining_time * 0.15
    elif moves_made < 30:
        return remaining_time * 0.10
    else:
        return remaining_time * 0.05
```

## 4. 実装推奨事項

### 4.1 アーキテクチャ設計
```python
class OptimalAI(Alg3D):
    def __init__(self):
        self.transposition_table = TranspositionTable()
        self.opening_book = OpeningBook()
        self.evaluator = PositionEvaluator()
    
    def get_move(self, board, player, last_move):
        # 1. 定跡チェック
        if opening_move := self.opening_book.get_move(board):
            return opening_move
            
        # 2. 即座勝利チェック
        if winning_move := self.find_winning_move(board, player):
            return winning_move
            
        # 3. 脅威ブロック
        if blocking_move := self.find_blocking_move(board, player):
            return blocking_move
            
        # 4. Minimax探索
        return self.minimax_search(board, player)
```

### 4.2 デバッグ・テスト戦略
- **単体テスト**: 各評価関数の正確性
- **勝利パターンテスト**: 76種の勝利ライン検出
- **パフォーマンステスト**: 制限時間内での応答確認
- **対戦テスト**: 異なる強度のAI間での比較

### 4.3 パフォーマンス目標
- **探索深度**: 平均7手先
- **応答時間**: 平均3秒以内  
- **勝率**: ランダムプレイヤー対99%以上
- **メモリ使用量**: 500MB以内

## 5. 結論

4×4×4立体四目並べの最適解は、**Minimax + Alpha-Beta + 高度な評価関数**の組み合わせが最も有効である。特に、76の勝利ラインを効率的に評価し、中心制御と高度優位性を重視した戦略が推奨される。

実装時は制限時間とメモリ制約を考慮し、Iterative DeepeningとTransposition Tableを活用した段階的な探索深度拡張が重要となる。