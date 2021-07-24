from coganh.chess_board import ChessBoard
from coganh.config import BG_COLOR, BOARD_SIZE, CHESS_SIZE, P1_COLOR, P2_COLOR
from coganh.utils import Screen
import tkinter as tk
import tkinter.ttk as ttk

class BatchScreen(Screen):
    def __init__(self, *args, **kwargs):
        Screen.__init__(self, *args, **kwargs)
        label = ttk.Label(self, text="TBD")
        label.pack(side="top", fill="both", expand=True)
        ttk.Button(self, text="Main", command=lambda: self.root.navigator.pop()).pack()
