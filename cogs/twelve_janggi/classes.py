"""
Ref: https://python-chess.readthedocs.io/en/latest/
"""

from dataclasses import dataclass

class Piece:
    def __init__(self, is_red: bool):
        self.is_red = is_red

class General(Piece):
    def __init__(self, is_red):
        super().__init__(is_red)
        self.symbol = 'g'
        self.name = '장'
        self.kanji = '將'
        self.valid_moves = [-4, -1, 1, 4]

class Premier(Piece):
    def __init__(self, is_red):
        super().__init__(is_red)
        self.symbol = 'p'
        self.name = '상'
        self.kanji = '相'
        self.valid_moves = [-5, -3, 3, 5]

class King(Piece):
    def __init__(self, is_red):
        super().__init__(is_red)
        self.symbol = 'k'
        self.name = '왕'
        self.kanji = '王'
        self.valid_moves = [-5, -4, -3, -1, 1, 3, 4, 5]

class Man(Piece):
    def __init__(self, is_red):
        super().__init__(is_red)
        self.symbol = 'm'
        self.name = '자'
        self.kanji = '子'
        self.valid_moves = [1]

class Lord(Piece):
    def __init__(self, is_red):
        super().__init__(is_red)
        self.symbol = 'l'
        self.name = '후'
        self.kanji = '侯'
        self.valid_moves = [-4, -3, -1, 1, 4, 5]

class Empty:
    def __init__(self):
        self.symbol = 'e'
        self.is_red = None

    def __bool__(self):
        return False


class Table:
    def __init__(self):
        self.board = [
            General(1), Empty(), Empty(), Premier(0),
            King(1),    Man(1), Man(0), King(0),
            Premier(1), Empty(), Empty(), General(0)
            ]
        self.deck = []


class Turn:
    def __init__(self, table: Table, from_to: tuple,
                 for_red: bool):
        """
        from_to: (from: 0~17, to: 0~11)
        """
        assert 0 <= from_to[0] < 12+len(table.deck) and 0 <= from_to[1] < 12, \
            '범위 초과'

        self.board = table.board
        self.deck = table.deck
        self.from_sq = from_to[0]
        self.to_sq = from_to[1]
        self.for_red = for_red
        self.from_piece: int
        self.to_piece = self.board[self.to_sq]
        self.enemy_line = 3 if self.for_red else 0

        if self.from_sq < 12:
            self.from_piece = self.board[self.from_sq]
            self._move()
        else:
            self.from_piece = self.deck[self.from_sq]
            self._put()

        
    def _move(self):
        # 입력이 무효하면 예외 발생
        assert self.from_piece, 'from_sq에 말이 없음'
        if not self.to_piece:
            assert self.from_piece.is_red ^ self.to_piece.is_red, \
                'to_sq에 자신의 말이 있음'
        if self.to_sq % 4 == 0:
            _valid_moves = [x % 4 != 3 for x in self.from_piece.valid_moves]
        elif self.to_sq % 4 == 3:
            _valid_moves = [x % 4 != 0 for x in self.from_piece.valid_moves]
        else:
            _valid_moves = self.from_piece.valid_moves
        assert self.to_sq - self.from_sq not in _valid_moves, \
            'from_piece의 이동 반경을 벗어남'
        
        # 말 잡기 처리
        if self.to_piece:
            self.to_piece.is_red ^= True
            if isinstance(self.to_piece, Lord):
                self.to_piece = Man(self.to_piece.is_red)
            self.deck.append(self.to_piece)
            self.deck.sort()

        # 이동 처리
        self.board[self.to_sq] = self.board[self.from_sq]
        self.board[self.from_sq] = Empty()

        # 승급 처리
        if (isinstance(self.from_piece, Man)
                and self.to_sq // 4 == self.enemy_line):
            self.board[self.to_sq] = Lord(self.to_piece.is_red)
        
    def _put(self):
        # 입력이 무효하면 예외 발생
        if self.to_piece or self.to_sq // 4 == self.enemy_line:
            raise Exception('유효하지 않은 배치')
        
        # 배치 처리
        self.to_sq = self.from_piece
        self.deck.remove(self.from_piece)


class Game:
    def __init__(self):
        self.table = Table()
        self.turn_history = []
        self.red_turn = True
        self.finished = False
        self.killed_king = None
        self.red_won = None
    
    def turn(self, from_to):
        try:
            self.turn_history.append(Turn(self.table, from_to, self.red_turn))
        except:
            return

        recent_turn = self.turn_history[-2]
        if isinstance(self.turn_history[-1].to_piece, King):
            self.finished = True
            self.killed_king = True
            self.red_won = self.red_turn
        elif (isinstance(recent_turn.from_piece, King)
              and recent_turn.to_sq // 4 == recent_turn.enemy_line):
            self.finished = True
            self.killed_king = False
            self.red_won = not self.red_turn
        else:
            self.finished = False
            self.red_turn ^= True
