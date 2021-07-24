from coganh.chess_board import ChessBoard
from coganh.player import Player
import tkinter as tk
import tkinter.ttk as ttk
from typing import List
from coganh.main_screen import MainScreen
from coganh.play_screen import PlayScreen
from coganh.batch_screen import BatchScreen
from coganh.navigator import Navigator
from coganh.config import BG_COLOR, FONT, P1_COLOR, P2_COLOR

class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Cờ Gánh")
        self.geometry("800x600")
        # Intialize players
        Player(1, "Người chơi 1", P1_COLOR)
        Player(-1, "Người chơi 2", P2_COLOR)
        self.players = Player.connect()
        # Create screens
        self.play = PlayScreen(self)
        self.batch = BatchScreen(self)
        self.main = MainScreen(self)
        # Config UI
        self.style = ttk.Style()
        self.style.configure('TFrame', background=BG_COLOR)
        self.style.configure('TLabel', background=BG_COLOR)
        self.style.configure(
            'TButton', padding=10, width=20, background=BG_COLOR, font=FONT
        )
        self.style.configure('TCombobox', arrowsize=18, font=FONT)
        # Show main screen
        self.navigator = Navigator()
        self.navigator.push(self.main)

    def run(self):
        self.mainloop()