from coganh.config import RULE
from coganh.utils import boardHelper, symmetricHelper

class Logic:
    @staticmethod
    def checkValidMove(move) -> bool:
        (fx, fy) = move[0]
        (tx, ty) = move[1]
        if ((ty, tx) in boardHelper[fy][fx]):
            return True
        else:
            return False

    @staticmethod
    def getBoardAfterMove(board, player, pos, rule=RULE):
        (x, y) = pos
        unvisit = list.copy(boardHelper[x][y])
        isEaten = False
        # Get "Gánh" chessmans
        if rule & 0b100 == 0b100:
            isEaten |= Logic._eatBySymmetries(board, player, pos, unvisit)
        # Get "Chẹt" chessmans
        if rule & 0b010 == 0b010:
            for chessPos in unvisit:
                (cx, cy) = chessPos
                chessPlayer = board[cy][cx]
                if player != chessPlayer:
                    isEaten |= Logic._eatBySymmetries(board, player, chessPos,
                        unvisit, pos)
                else:
                    unvisit.remove(chessPos)
        # Get "Vây" chessmans
        if rule & 0b001 == 0b001:
            for i in range(5):
                for j in range(5):
                    visitted = set()
                    chessPlayer = board[j][i]
                    if (chessPlayer != 0 and chessPlayer != player
                            and not Logic._getUnmoveChessList(board, chessPlayer,
                            (i, j), visitted)):
                        for changePos in visitted:
                            (px, py) = changePos
                            board[py][px] = player
                            isEaten |= True
        return isEaten

    @staticmethod
    def _getUnmoveChessList(board, curChessPlayer, pos, visitted):
        if pos in visitted:
            return False
        visitted.add(pos)
        (x, y) = pos
        helper = boardHelper[x][y]
        rt = False
        i = 0
        n = len(helper)
        while i < n and not rt:
            (px, py) = helper[i]
            chessPlayer = board[py][px]
            if chessPlayer == 0:
                rt = rt or True
            elif chessPlayer == curChessPlayer:
                rt = rt or Logic._getUnmoveChessList(board, curChessPlayer,
                    helper[i], visitted)
            i += 1
        return rt

    @staticmethod
    def _eatBySymmetries(board, player, pos, unvisit, center = None):
        isEaten = False
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
                    isEaten |= True
                    board[y1][x1] = player
                    board[y2][x2] = player
                    unvisit.remove(sym[0])
                    unvisit.remove(sym[1])
                elif center is not None:
                    isEaten |= True
                    board[y][x] = player
                    unvisit.remove(pos)
        return isEaten

    @staticmethod
    def isTrapChess(board, fromPos, toPos):
        (fx, fy) = fromPos
        (tx, ty) = toPos
        symmetries = symmetricHelper[fx][fy]
        for sym in symmetries:
            if toPos in sym:
                if toPos == sym[0]:
                    (sx, sy) = sym[1]
                else:
                    (sx, sy) = sym[0]
                if board[sy][sx] == board[ty][tx]:
                    helper = boardHelper[fx][fy]
                    for point in helper:
                        (px, py) = point
                        if board[py][px] == -board[ty][tx]:
                            return True
                break
        return False

    @staticmethod
    def getMovableChessList(board, player, trapPos):
        movableList = []
        # Get chess is trapped if exist
        if trapPos is not None:
            (trX, trY) = trapPos
            helper = boardHelper[trX][trY]
            for point in helper:
                (px, py) = point
                chessPlayer = board[py][px]
                if player == chessPlayer:
                    movableList.append(point)
            if len(movableList) > 0:
                return movableList
        # Get all player chess
        for i in range(5):
            for j in range(5):
                if board[j][i] == player:
                    point = (i, j)
                    if Logic.isMovableChess(board, point):
                        movableList.append(point)
        return movableList

    @staticmethod
    def isMovableChess(board, chessPos):
        (x, y) = chessPos
        moveList = boardHelper[x][y]
        for point in moveList:
            (px, py) = point
            if board[py][px] == 0:
                return True
        return False

    @staticmethod
    def getMovablePositionList(board, pos, trapPos):
        movablePosList = []
        if trapPos is not None:
            movablePosList.append(trapPos)
        else:
            (x, y) = pos
            helper = boardHelper[x][y]
            for point in helper:
                (px, py) = point
                if board[py][px] == 0:
                    movablePosList.append(point)
        return movablePosList