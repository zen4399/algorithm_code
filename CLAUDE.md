# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Testing and Development
- `python local_driver.py` - Test your AI implementation locally with stub board data
- `python main.py` - Direct execution (not recommended; use local_driver.py instead)

### Local Testing Process
The local testing workflow uses the driver system:
1. Modify `stub_board.py` to set up test scenarios (board state, player, last_move)
2. Run `python local_driver.py` to test your AI's next move
3. The driver will load your `MyAI` class from `main.py` and call `get_move()`

## Architecture

This is a 3D Connect Four (立体四目並べ) AI competition codebase with the following structure:

### Core Files
- `main.py` - Main AI implementation file containing the `MyAI` class
- `local_driver.py` - Local testing framework that loads and tests AI implementations  
- `stub_board.py` - Test data configuration (board state, player, last move)

### Key Components

**Board Representation**: 3D array structure `List[List[List[int]]]`
- Dimensions: 4x4x4 (z, y, x coordinates)
- Values: 0=empty, 1=player1/black, 2=player2/white
- Gravity applies: pieces fall to lowest available z-level in each (x,y) column

**AI Interface**: All AIs must inherit from `Alg3D` abstract base class
- Required method: `get_move(board, player, last_move) -> Tuple[int, int]`
- Returns (x, y) coordinates where x,y are in range 0-3
- The framework handles z-coordinate placement via gravity

**Local Testing Framework**: 
- `local_driver.py` provides the testing infrastructure
- Imports the AI class dynamically from `main.py`
- Uses stub data from `stub_board.py` for consistent testing
- Validates AI implementation and method signatures

### Development Notes

**Submission Requirements**:
- Must use Python 3.9 compatible syntax (no match statements)
- Only Python standard library allowed (with specific restrictions)
- Execution limits: ~1GB memory, ~3 seconds CPU time, 10 seconds per move
- Invalid moves result in automatic placement from top-left

**Import Structure**:
- Local testing: `from local_driver import Alg3D, Board`
- Production: `from framework import Alg3D, Board` (commented out in template)

**Testing Strategy**:
- Modify `stub_board.py` to create different board scenarios
- Test edge cases: full columns, win conditions, timeout scenarios
- Validate move validity within 0-3 coordinate bounds