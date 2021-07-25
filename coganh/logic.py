from coganh.player import Player
from coganh.config import RULE
from coganh.utils import boardHelper, symmetricHelper

class Logic:
    @staticmethod
    def checkValidMove(board, move) -> bool:
        (fx, fy) = move[0]
        (tx, ty) = move[1]
        if ((ty, tx) in boardHelper[fy][fx]
            and board[fy][fx] != 0
            and board[ty][tx] == 0
        ):
            return True
        else:
            return False

    @staticmethod
    def getBoardAfterMove(board, player, pos, rule=RULE):
        (x, y) = pos
        unvisit = list.copy(boardHelper[x][y])
        # Get "Gánh" chessmans
        if rule & 0b100 == 0b100:
            Logic._eatBySymmetries(board, player, pos, unvisit)
        # Get "Chẹt" chessmans
        if rule & 0b010 == 0b010:
            for chessPos in unvisit:
                (cx, cy) = chessPos
                chessPlayer = board[cy][cx]
                if player != chessPlayer:
                    Logic._eatBySymmetries(board, player, chessPos, unvisit,
                        pos)
                else:
                    unvisit.remove(chessPos)
        # Get "Vây" chessmans
        if rule & 0b001 == 0b001:
            for i in range(5):
                for j in range(5):
                    visitted = set()
                    chessPlayer = board[j][i]
                    if (chessPlayer != 0 and chessPlayer != player
                            and not Logic._getUnmoveChesses(board, chessPlayer,
                            (i, j), visitted)):
                        for changePos in visitted:
                            (px, py) = changePos
                            board[py][px] = player

    @staticmethod
    def _getUnmoveChesses(board, curChessPlayer, pos, visitted):
        if pos in visitted:
            return False
        visitted.add(pos)
        (x, y) = pos
        helper = boardHelper[x][y]
        rt = False
        for point in helper:
            (px, py) = point
            chessPlayer = board[py][px]
            if chessPlayer == 0:
                rt = rt or True
            elif chessPlayer == curChessPlayer:
                rt = rt or Logic._getUnmoveChesses(board, curChessPlayer, point,
                    visitted)
            if rt == True:
                break
        return rt


    @staticmethod
    def _eatBySymmetries(board, player, pos, unvisit, center = None):
        (x, y) = pos
        symmetries = symmetricHelper[x][y]
        if center is not None:
            (cx, cy) = center
        for sym in symmetries:
            (x1, y1) = sym[0]
            (x2, y2) = sym[1]
            chess1Player = board[y1][x1]
            chess2Player = board[y2][x2]
            if chess1Player == 0 or chess2Player == 0:
                if chess1Player == 0 and sym[0] in unvisit:
                    unvisit.remove(sym[0])
                if chess2Player == 0 and sym[1] in unvisit:
                    unvisit.remove(sym[1])
                continue
            if (center is not None and (cx != x1 or cy != y1)
                    and (cx != x2 or cy != y2)):
                continue
            if chess1Player == chess2Player:
                if player != chess1Player:
                    board[y1][x1] = player
                    board[y2][x2] = player
                    unvisit.remove(sym[0])
                    unvisit.remove(sym[1])
                elif center is not None:
                    board[y][x] = player
                    unvisit.remove(pos)