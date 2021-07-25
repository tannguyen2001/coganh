from os import remove
from coganh.config import LINE_WIDTH, P1_COLOR
from coganh.player import Player
from coganh.utils import boardHelper

class Chessman:
    id: int
    player: Player
    def __init__(self, id, player, pos, board):
        self.id = id
        self.board = board
        self.player = player
        (self.x, self.y) = pos

    def onMove(self, toPos):
        (fromX, fromY) = (self.x, self.y)
        (self.x, self.y) = (toX, toY) = toPos
        (self.board[toY][toX], self.board[fromY][fromX]) = (
            self.board[fromY][fromX], self.board[toY][toX]
        )

    def onEaten(self):
        self.player = self.player.opposite

    def canMove(self, visitted):
        if self in visitted:
            return False
        visitted.add(self)
        helper = boardHelper[self.x][self.y]
        rt = False
        for point in helper:
            (x, y) = point
            chess = self.board[y][x]
            if chess is None:
                rt = rt or True
            elif chess.player is self.player:
                rt = rt or chess.canMove(visitted)
            if rt == True:
                break
        return rt
