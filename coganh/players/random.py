import random
RULE = 0b101

encodedBoardHelper = [
    [(0,0), (1,0), (2,0), (1,0), (0,1)],
    [(1,3), (4,0), (3,0), (4,0), (1,1)],
    [(2,3), (3,0), (4,0), (3,0), (2,1)],
    [(1,3), (4,0), (3,0), (4,0), (1,1)],
    [(0,3), (1,2), (2,2), (1,2), (0,2)]
]
directValue = [
    (-1,-1), (-1, 0), (-1, 1),
    ( 0,-1), ( 0, 0), ( 0, 1),
    ( 1,-1), ( 1, 0), ( 1, 1)
]
boardDirect = [
    [[5,8,7], [7,6,3], [3,0,1], [1,2,5]],
    [[5,7,3], [7,3,1], [3,1,5], [1,5,7]],
    [[5,7,3,8,6], [7,3,1,6,0], [3,1,5,0,2], [1,5,7,2,8]],
    [[1,3,5,7]],
    [[0,1,2,3,5,6,7,8]]
]
symmetricPoint = [
    [[], [], [], []],
    [[(5,3)], [(7,1)], [(3,5)], [(1,7)]],
    [[(5,3)], [(7,1)], [(3,5)], [(1,7)]],
    [[(3,5),(1,7)]],
    [[(0,8),(1,7),(3,5),(2,6)]]
]

boardHelper = []
symmetricHelper = []
for i in range(5):
    boardHelper.append([])
    symmetricHelper.append([])
    for j in range(5):
        helper = encodedBoardHelper[i][j]
        indexes = boardDirect[helper[0]][helper[1]]
        directs = [directValue[x] for x in indexes]
        xy = [(x[0]+i,x[1]+j) for x in directs] 
        symIndexes = symmetricPoint[helper[0]][helper[1]]
        symmetrics = [(directValue[x[0]], directValue[x[1]]) for x in symIndexes]
        symXy = [[(x[0]+i,x[1]+j) for x in y] for y in symmetrics] 
        boardHelper[i].append(xy)
        symmetricHelper[i].append(symXy)

class LocalLogic:
    @staticmethod
    def getBoardAfterMove(board, player, pos, rule=RULE):
        (x, y) = pos
        unvisit = list.copy(boardHelper[x][y])
        isEaten = False
        # Get "Gánh" chessmans
        if rule & 0b100 == 0b100:
            isEaten |= LocalLogic._eatBySymmetries(board, player, pos, unvisit)
        # Get "Chẹt" chessmans
        if rule & 0b010 == 0b010:
            for chessPos in unvisit:
                (cx, cy) = chessPos
                chessPlayer = board[cy][cx]
                if player != chessPlayer:
                    isEaten |= LocalLogic._eatBySymmetries(board, player, chessPos,
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
                            and not LocalLogic._getUnmoveChessList(board, chessPlayer,
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
                rt = rt or LocalLogic._getUnmoveChessList(board, curChessPlayer,
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
    def getOpponentChess(oldBoard, newBoard):
        fromPos = None
        toPos = None
        for i in range(5):
            for j in range(5):
                if oldBoard[j][i] == 0 and newBoard[j][i] != 0:
                    toPos = (i, j)
                elif oldBoard[j][i] != 0 and newBoard[j][i] == 0:
                    fromPos = (i, j)
        return (fromPos, toPos)

    @staticmethod
    def isEaten(oldBoard, newBoard):
        for i in range(5):
            for j in range(5):
                if oldBoard[j][i] == -newBoard[j][i] != 0:
                    return True
        return False

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
                    if LocalLogic.isMovableChess(board, point):
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

oldBoardMap = {-1: None, 1: None}

def move(board, player):
    global oldBoardMap
    oldBoard = oldBoardMap[player]
    trapPos = None
    if oldBoard is not None and not LocalLogic.isEaten(oldBoard, board) :
        opponentMove = LocalLogic.getOpponentChess(oldBoard, board)
        if opponentMove[0] is not None and opponentMove[1] is not None:
            ((fx, fy), (tx, ty)) = opponentMove
            if (tx, ty) not in boardHelper[fx][fy]:
                print("----Reset1----")
            elif LocalLogic.isTrapChess(board, *opponentMove):
                trapPos = opponentMove[0]
        else:
            print("----Reset2----")
    oldBoard = [list.copy(x) for x in board]
    fList = LocalLogic.getMovableChessList(board, player, trapPos)
    f = random.choice(fList)
    if trapPos is not None:
        t = tuple(trapPos)
    else:
        toMoveList = [x for x in boardHelper[f[0]][f[1]] if board[x[1]][x[0]] == 0]
        t = random.choice(toMoveList)
    print(f"From {f[::-1]} to {t[::-1]}")
    oldBoard[f[1]][f[0]], oldBoard[t[1]][t[0]] = oldBoard[t[1]][t[0]], oldBoard[f[1]][f[0]]
    LocalLogic.getBoardAfterMove(oldBoard, player, (t[0], t[1]))
    oldBoardMap[player] = oldBoard
    return ((f[1], f[0]), (t[1], t[0]))