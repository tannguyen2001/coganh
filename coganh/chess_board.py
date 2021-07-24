from coganh.player import Player
from typing import List
from coganh.chessman import Chessman
from coganh.config import BG_COLOR, BOARD_SIZE, CHESS_SIZE, CHET_RULE, GANH_RULE, HINT_COLOR, LINE_COLOR, VAY_RULE
from coganh.config import LINE_WIDTH, P1_COLOR, P2_COLOR, POINT_SIZE
from coganh.utils import toLogicalPosition, toVisualPosition, initialBoard
from coganh.utils import boardHelper, symmetricHelper, PlayingTimeoutError
import threading
import tkinter.messagebox as mes
import tkinter as tk

class ChessBoard(tk.Canvas):
    board: List[List[Chessman]]
    player: Player
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.parent = args[0]
        # Draw board 4 border lines
        self.drawLine((0,0),(0,4),width=LINE_WIDTH, fill=LINE_COLOR)
        self.drawLine((0,0),(4,0),width=LINE_WIDTH, fill=LINE_COLOR)
        self.drawLine((0,4),(4,4),width=LINE_WIDTH, fill=LINE_COLOR)
        self.drawLine((4,0),(4,4),width=LINE_WIDTH, fill=LINE_COLOR)
        # Draw board 2 long diagonal lines
        self.drawLine((0,0),(4,4),width=LINE_WIDTH, fill=LINE_COLOR)
        self.drawLine((0,4),(4,0),width=LINE_WIDTH, fill=LINE_COLOR)
        # Draw board 6 middle lines
        self.drawLine((0,2),(4,2),width=LINE_WIDTH, fill=LINE_COLOR)
        self.drawLine((2,0),(2,4),width=LINE_WIDTH, fill=LINE_COLOR)
        self.drawLine((0,1),(4,1),width=LINE_WIDTH, fill=LINE_COLOR)
        self.drawLine((1,0),(1,4),width=LINE_WIDTH, fill=LINE_COLOR)
        self.drawLine((0,3),(4,3),width=LINE_WIDTH, fill=LINE_COLOR)
        self.drawLine((3,0),(3,4),width=LINE_WIDTH, fill=LINE_COLOR)
        # Draw board 4 long diagonal lines
        self.drawLine((0,2),(2,4),width=LINE_WIDTH, fill=LINE_COLOR)
        self.drawLine((2,4),(4,2),width=LINE_WIDTH, fill=LINE_COLOR)
        self.drawLine((4,2),(2,0),width=LINE_WIDTH, fill=LINE_COLOR)
        self.drawLine((2,0),(0,2),width=LINE_WIDTH, fill=LINE_COLOR)
        # Draw board 25 mini point
        for i in range(5):
            for j in range(5):
                self.drawCircle((i,j),POINT_SIZE,fill=BG_COLOR,width=LINE_WIDTH)
        # Initialize board with None
        self.board = []
        for i in range(5):
            self.board.append([])
            for _ in range(5):
                self.board[i].append(None)
        self.initialBoard = initialBoard
        # Bind onclick action
        self.bind('<Button-1>', self.onClick)
        self.chessmanToMove = None
        # Status of game
        self.isPlaying = False
        self.forceFinish = False
        self.pack()

    def startGame(self):
        self.resetBoard()
        self.isPlaying = True
        self.thread = threading.Thread(target=self.playGame, daemon=True)
        self.thread.start()

    def playGame(self):
        while not self.isFinish():
            self.callNext()
        else:
            self.isPlaying = False

    def callNext(self):
        self.player = Player.next()
        # Get covered chessmans
        if VAY_RULE:
            for row in self.board:
                for chess in row:
                    visitted = set()
                    if (chess is not None and chess.player is self.player
                            and not chess.canMove(visitted)):
                        for changePoint in visitted:
                            changePos = (changePoint.x, changePoint.y)
                            self.eatChessman(changePos)
        if self.isFinish():
            return
        board = self.getSummaryBoard()
        player = self.player.id
        print(f"Turn of '{self.player.label}'")
        event = threading.Event()
        try:
            if not self.player.isMan():
                def moveFunc():
                    self.moveLogic = self.player.move(board, player)
                    event.set()
                thread = threading.Thread(target=moveFunc, daemon=True)
                thread.start()
                if not event.wait(3):
                    raise PlayingTimeoutError()
                moveLogic = self.moveLogic
            else:
                moveLogic = self.player.move(board, player)
            if moveLogic is None:
                return
            (fromPos, toPos) = moveLogic
            move = ((fromPos[1], fromPos[0]), (toPos[1], toPos[0]))
            self.moveChessman(*move)
            self.eatChessmans(move[1])
        except PlayingTimeoutError:
            self.forceFinish = True
            print("Player take too much time to play")
        except Exception as e:
            print(e)
            raise

    def getSummaryBoard(self):
        sumBoard = []
        for i in range(5):
            sumBoard.append([])
            for j in range(5):
                if type(self.board[i][j]) is Chessman:
                    sumBoard[i].append(self.board[i][j].player.id)
                else:
                    sumBoard[i].append(0)
        return sumBoard


    def calculateF(self):
        board = self.getSummaryBoard()
        f = 0
        for row in board:
            for col in row:
                f += col
        return f

    def isFinish(self):
        f = self.calculateF()
        return f == 16 or f == -16 or self.forceFinish or not self.isPlaying

    """
    * Draw line by logical position
    * Input:
    * - fromLogical: tuple(x, y) logical position of start of line
    * - toLogical: tuple(x, y) logical position of end of line
    * - **kwargs: option to pass to Canvas create line object
    * Output:
    * - CanvasItemId: the Id of line object
    * Process:
    * - Draw a new line from fromLogical to toLogical position
    """
    def drawLine(self, fromLogical, toLogical, **kwargs):
        fromx, fromy = toVisualPosition(*fromLogical)
        tox, toy = toVisualPosition(*toLogical)
        return self.create_line(fromx, fromy, tox, toy, **kwargs)

    """
    * Draw circle by logical position
    * Input:
    * - logicalPos: tuple(x, y): logical position of center of circle
    * - size: int: size of the circle
    * - **kwargs: option to pass to Canvas create line object
    * Output:
    * - CanvasItemId: the Id of circle object
    * Process:
    * - Draw a new circle at position
    """
    def drawCircle(self, logicalPos, size, **kwargs):
        r = size/2
        x, y = toVisualPosition(*logicalPos)
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

    def createChessman(self, playerId, logicalPos, **kwargs):
        player1: Player = Player.playerList[0]
        player2: Player = Player.playerList[1]
        if playerId == player1.id or playerId == player2.id:
            if playerId == player1.id:
                player = player1
            else:
                player = player2
            id = self.drawCircle(
                logicalPos, CHESS_SIZE, fill=player.color, width=0,
                outline=player.color, tag='chessman', **kwargs
            )
            return Chessman(id, player, logicalPos, self.board)
        else:
            return None

    def moveChessman(self, fromLogical, toLogical, **kwargs):
        (fx, fy) = fromLogical
        (tx, ty) = toLogical
        if ((ty, tx) in boardHelper[fy][fx]
            and self.board[fy][fx] is not None
            and self.board[ty][tx] is None
        ):
            self.clearTemp()
            fromx, fromy = toVisualPosition(*fromLogical)
            tox, toy = toVisualPosition(*toLogical)
            chessman = self.board[fy][fx]
            chessman.onMove(toLogical)
            self.drawLine(
                fromLogical, toLogical, width=LINE_WIDTH*3, fill=HINT_COLOR,
                tag='temp'
            )
            self.drawCircle(
                fromLogical, POINT_SIZE, fill=HINT_COLOR, width=LINE_WIDTH,
                outline=HINT_COLOR, tag='temp'
            )
            self.move(chessman.id, tox-fromx, toy-fromy, **kwargs)
            self.lift(chessman.id)
        else:
            self.player = Player.prev()
            print("Failed to move")

    def eatChessmans(self, pos):
        (x, y) = pos
        unvisit = list.copy(boardHelper[x][y])
        changed = set()
        # Get carried chessmans
        if GANH_RULE:
            self.eatBySymmetries(pos, unvisit, changed)
        # Get carrying chessmans
        if CHET_RULE:
            for chessPos in unvisit:
                (cx, cy) = chessPos
                chess = self.board[cy][cx]
                if chess is None or chessPos in changed:
                    unvisit.remove(chessPos)
                    continue
                if self.player is not chess.player:
                    self.eatBySymmetries(chessPos, unvisit, changed, pos)

    def eatBySymmetries(self, pos, unvisit, changed, center = None):
        (x, y) = pos
        symmetries = symmetricHelper[x][y]
        if center is not None:
            (cx, cy) = center
            centerChess = self.board[cy][cx]
        for sym in symmetries:
            (x1, y1) = sym[0]
            (x2, y2) = sym[1]
            chess1 = self.board[y1][x1]
            chess2 = self.board[y2][x2]
            if chess1 is None or chess2 is None:
                if chess1 is None and sym[0] in unvisit:
                    unvisit.remove(sym[0])
                if chess2 is None and sym[1] in unvisit:
                    unvisit.remove(sym[1])
                continue
            if (center is not None and chess1 is not centerChess
                    and chess2 is not centerChess):
                continue
            c1Player = chess1.player
            c2Player = chess2.player
            if c1Player is c2Player:
                if self.player is not c1Player:
                    if sym[0] not in changed and sym[1] not in changed:
                        self.eatChessman(sym[0])
                        self.eatChessman(sym[1])
                        unvisit.remove(sym[0])
                        unvisit.remove(sym[1])
                        changed.add(sym[0])
                        changed.add(sym[1])
                elif center is not None:
                    if pos not in changed:
                        self.eatChessman(pos)
                        unvisit.remove(pos)
                        changed.add(pos)

    def eatChessman(self, pos):
        (x, y) = pos
        chess = self.board[y][x]
        chess.onEaten()
        self.addtag_withtag("eatenChess", chess.id)
        self.itemconfig(chess.id, fill=chess.player.color,
            outline=chess.player.next.color, width=LINE_WIDTH)

    def onClick(self, event):
        if self.player.isMan() and self.isPlaying:
            if self.chessmanToMove is not None:
                (fx, fy) = self.chessmanToMove
                x, y = toLogicalPosition(event.x, event.y)
                r = CHESS_SIZE/2
                vx, vy = toVisualPosition(x, y)
                if (vx - r < event.x < vx + r
                    and vy - r < event.y < vy + r
                    and self.board[y][x] is None
                ):
                    print(f'Move from ({fy}, {fx}) to ({y}, {x})')
                    self.player.outputPos = ((fy,fx),(y,x))
                    self.player.isClicked.set()
                    #self.moveChessman((fx,fy),(x,y))
                elif self.board[y][x].player is self.player:
                    print(f'Click on ({y}, {x})')
                    self.chessmanToMove = (x, y)
                else:
                    self.chessmanToMove = None
            else:
                x, y = toLogicalPosition(event.x, event.y)
                r = CHESS_SIZE/2
                vx, vy = toVisualPosition(x, y)
                if (vx - r < event.x < vx + r
                    and vy - r < event.y < vy + r
                    and self.board[y][x] is not None
                    and self.board[y][x].player is self.player
                ):
                    print(f'Click on ({y}, {x})')
                    self.chessmanToMove = (x, y)
                else:
                    print("Failed to click")

    def onExit(self):
        if self.isPlaying and not mes.askyesno(
                title="Quay Lại Trang Chính",
                message="Bạn có muốn quay lại trang chính không?"
            ):
                return False
        self.forceFinish = True
        self.player.isClicked.set()
        self.thread.join(1)
        self.isPlaying = False
        self.destroy()
        return True

    def initializeBoard(self):
        # Draw board
        for i in range(5):
            for j in range(5):
                self.board[i][j] = self.createChessman(
                    self.initialBoard[i][j],(j,i)
                )

    def clearBoard(self):
        for i in range(5):
            for j in range(5):
                self.board[i][j] = None
        self.delete('chessman')

    def clearTemp(self):
        self.delete('temp')
        self.itemconfig("eatenChess", width=0)
        self.dtag("eatenChess", "eatenChess")

    def clearHint(self):
        self.delete('hint')

    def resetBoard(self):
        self.forceFinish = False
        Player.reset()
        self.clearTemp()
        self.clearBoard()
        self.initializeBoard()

    def pack(self):
        tk.Canvas.pack(self, padx=10, pady=10)