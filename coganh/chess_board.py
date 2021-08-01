from coganh.logic import Logic
from coganh.player import Player
from typing import List
from coganh.chessman import Chessman
from coganh.config import BG_COLOR, BOARD_SIZE, CHESS_SIZE, DISABLE_COLOR, HINT_COLOR, MOVE_COLOR, LINE_COLOR
from coganh.config import LINE_WIDTH, P1_COLOR, P2_COLOR, POINT_SIZE
from coganh.utils import ResetException, WrongMoveException, toLogicalPosition, toVisualPosition, initialBoard
from coganh.utils import boardHelper, symmetricHelper, PlayingTimeoutError
import threading
import tkinter.messagebox as mes
import tkinter as tk
import time

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
        # Bind onclick action
        self.bind('<Button-1>', self.onClick)
        self.chessmanToMove = None
        # Status of game
        self.forceFinish = False
        self.isPlaying = True
        self.player = Player.playerList[0]
        self.movableList = Logic.getMovableChessList(initialBoard, self.player.id, None)
        self.trapPos = None
        self.initializeBoard()
        self.thread = threading.Thread(target=self.playGame, daemon=True)
        self.thread.start()
        self.pack()

    def playGame(self):
        while not self.isFinish():
            self.callNext()
        else:
            self.isPlaying = False
        f = self.calculateF()
        if f == 16 or f == -16:
            self.clearTemp()
            print(f"'{self.player.opposite.label}' has won")

    def callNext(self):
        self.markHoverableChess()
        board = self.getSummaryBoard()
        player = self.player.id
        print(f"------ Turn '{self.player.label}' ------")
        event = threading.Event()
        startTime = time.time()
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
            if move[0] in self.movableList and Logic.checkValidMove(move):
                self.moveChessman(move)
                board = self.getSummaryBoard()
                # print("----Before----")
                # print(*board)
                isEaten = Logic.getBoardAfterMove(board, player, move[1])
                # print("----After----")
                # print(*board)
                self.parseBoardChange(board)
                if not isEaten and Logic.isTrapChess(board, *move):
                    self.trapPos = move[0]
                else:
                    self.trapPos = None
                self.movableList = Logic.getMovableChessList(board, self.player.opposite.id, self.trapPos)
            else:
                raise WrongMoveException()
        except PlayingTimeoutError:
            self.forceFinish = True
            print(f"'{self.player.label}' take too much time to play")
        except WrongMoveException:
            self.forceFinish = True
            print(f"'{self.player.label}' had a wrong move!")
            self.player.hasWrongMove()
            return
        except Exception as e:
            print(e)
            raise
        finally:
            self.player.addTime(time.time() - startTime)
            print(f"'{self.player.label}' had run in {self.player.getTime()}!")
        self.player = Player.next()

    def parseBoardChange(self, newBoard):
        for x in range(5):
            for y in range(5):
                if (self.board[y][x] is not None
                        and self.board[y][x].player.id != newBoard[y][x]):
                    self.eatChess((x, y))

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

    def moveChessman(self, move, **kwargs):
        (fx, fy) = move[0]
        (tx, ty) = move[1]
        self.clearTemp()
        fromx, fromy = toVisualPosition(fx, fy)
        tox, toy = toVisualPosition(tx, ty)
        chessman = self.board[fy][fx]
        chessman.onMove(move[1])
        self.drawLine(
            move[0], move[1], width=LINE_WIDTH*3, fill=MOVE_COLOR,
            tag='temp'
        )
        self.drawCircle(
            move[0], POINT_SIZE*3, fill=MOVE_COLOR, width=0, tag='temp'
        )
        self.move(chessman.id, tox-fromx, toy-fromy, **kwargs)
        self.lift(chessman.id)

    def eatChess(self, pos):
        (x, y) = pos
        chess = self.board[y][x]
        chess.onEaten()
        self.addtag_withtag("eatenChess", chess.id)
        self.itemconfig(chess.id, fill=chess.player.color,
            outline=chess.player.opposite.color, width=LINE_WIDTH*2)

    def markHoverableChess(self):
        for pos in self.movableList:
            (x, y) = pos
            chess = self.board[y][x]
            self.addtag_withtag("hoverChess", chess.id)
            self.itemconfig(chess.id, activefill=HINT_COLOR)
        for i in range(5):
            for j in range(5):
                chess = self.board[j][i]
                if (chess is not None
                        and chess.player == self.player
                        and (i, j) not in self.movableList):
                    self.addtag_withtag("disableChess", chess.id)
                    self.itemconfig(chess.id, fill=DISABLE_COLOR,
                        outline=chess.player.color, width=LINE_WIDTH*2)

    def hintClickedChess(self, pos):
        (x, y) = pos
        chess = self.board[y][x]
        self.addtag_withtag("clickedChess", chess.id)
        self.itemconfig(chess.id, outline=HINT_COLOR, width=LINE_WIDTH*2)
        board = self.getSummaryBoard()
        movablePosList = Logic.getMovablePositionList(board, pos, self.trapPos)
        for mPos in movablePosList:
            self.drawCircle(
                mPos, POINT_SIZE*3, fill=HINT_COLOR, width=0, tag='hint'
            )

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
                    and (self.trapPos is None or self.trapPos == (x, y))
                ):
                    print(f'Move from ({fy}, {fx}) to ({y}, {x})')
                    self.player.outputPos = ((fy,fx),(y,x))
                    self.player.isClicked.set()
                    self.trapPos = None
                elif ((x, y) in self.movableList):
                    print(f'Click on ({y}, {x})')
                    self.chessmanToMove = (x, y)
                else:
                    print("Failed to click")
                    self.chessmanToMove = None
            else:
                x, y = toLogicalPosition(event.x, event.y)
                r = CHESS_SIZE/2
                vx, vy = toVisualPosition(x, y)
                if (vx - r < event.x < vx + r
                    and vy - r < event.y < vy + r
                    and (x, y) in self.movableList
                ):
                    print(f'Click on ({y}, {x})')
                    self.chessmanToMove = (x, y)
                    self.hintClickedChess((x, y))
                else:
                    print("Failed to click")
            self.clearHint()
            if self.chessmanToMove is not None and self.board[y][x] is not None:
                self.hintClickedChess((x, y))

    def onExit(self):
        if self.isPlaying and not mes.askyesno(
                title="Quay Lại Trang Chính",
                message="Bạn có muốn quay lại trang chính không?"
            ):
                return False
        self.destroy()
        return True

    def destroy(self) -> None:
        self.forceFinish = True
        self.isPlaying = False
        self.player.isClicked.set()
        self.thread.join(1)
        Player.reset()
        return super().destroy()

    def initializeBoard(self):
        # Draw board
        for i in range(5):
            for j in range(5):
                self.board[i][j] = self.createChessman(
                    initialBoard[i][j],(j,i)
                )

    def clearTemp(self):
        self.delete('temp')
        self.itemconfig("eatenChess", width=0)
        self.dtag("eatenChess", "eatenChess")
        self.itemconfig("hoverChess", activefill='')
        self.dtag("hoverChess", "hoverChess")
        self.itemconfig("disableChess", fill=self.player.color, width=0)
        self.dtag("disableChess", "disableChess")
        self.clearHint()

    def clearHint(self):
        self.itemconfig("clickedChess", width=0)
        self.dtag("clickedChess", "clickedChess")
        self.delete('hint')

    def pack(self):
        tk.Canvas.pack(self, padx=10, pady=10)