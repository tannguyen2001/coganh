from coganh.chess_board import ChessBoard
from coganh.config import BG_COLOR, BOARD_SIZE, CHESS_SIZE, P1_COLOR, P2_COLOR
from coganh.utils import Screen, ScreenFrame
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as mes

class PlayScreen(Screen):
    def __init__(self, *args, **kwargs):
        Screen.__init__(self, *args, **kwargs)
        # Create widgets
        self.main = PlayMain(self.root, self)
        self.side = PlaySideBar(self.root, self)
    def place(self):
        # Initalize board
        self.root.board = self.createBoard()
        return super().place()
    def createBoard(self):
        size = BOARD_SIZE+CHESS_SIZE+4
        return ChessBoard(
            self.root.play.main.mainBoard, width=size, height=size, bg=BG_COLOR,
            bd=0, highlightthickness=0
        )
    def resetBoard(self):
        self.root.board.destroy()
        self.root.board = self.createBoard()

class PlayMain(ScreenFrame):
    def __init__(self, *args, **kwargs):
        ScreenFrame.__init__(self, *args, **kwargs)
        # Create widgets
        self.top = PlayMainTop(self.root, self)
        self.mainBoard = PlayMainBoard(self.root, self)
        self.pack()
    def pack(self):
        ScreenFrame.pack(self, side='left', fill='both', expand=True)

class PlayMainTop(ScreenFrame):
    def __init__(self, *args, **kwargs):
        ScreenFrame.__init__(self, *args, **kwargs)
        self.pack()
    def pack(self):
        ScreenFrame.pack(self, side='top', fill='both', expand=True)

class PlayMainBoard(ScreenFrame):
    def __init__(self, *args, **kwargs):
        ScreenFrame.__init__(self, *args, **kwargs)
        self.pack()
    def pack(self):
        ScreenFrame.pack(self, side='top', fill='both', expand=True)

class PlaySideBar(ScreenFrame):
    def __init__(self, *args, **kwargs):
        ScreenFrame.__init__(self, *args, **kwargs)
        # Create buttons
        self.auto = ResetButton(self, text="Làm mới", command=self.reset)
        self.back = BackButton(
            self, text="Quay Lại",
            command=self.callback
        )
        self.pack()
    def callback(self):
        board: ChessBoard = self.root.board
        if board.onExit():
            self.root.navigator.pop()
    def reset(self):
        return self.root.play.resetBoard()
    def pack(self):
        ScreenFrame.pack(self, side='left', fill='both', expand=True)

class SideBarButton(ttk.Button):
    def __init__(self, *args, **kwargs):
        ttk.Button.__init__(self, *args, **kwargs)
    def pack(self):
        ttk.Button.pack(self, padx=10, pady=10, side='top', fill='x')

class ResetButton(SideBarButton):
    def __init__(self, *args, **kwargs):
        ttk.Button.__init__(self, *args, **kwargs)
        self.pack()

class BackButton(SideBarButton):
    def __init__(self, *args, **kwargs):
        ttk.Button.__init__(self, *args, **kwargs)
        self.pack()