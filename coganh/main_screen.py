from coganh.player import Player
import tkinter as tk
import tkinter.ttk as ttk
from coganh.utils import Screen, ScreenFrame
from coganh.config import P1_COLOR, P2_COLOR, BG_COLOR

class MainScreen(Screen):
    def __init__(self, *args, **kwargs):
        Screen.__init__(self, *args, **kwargs)
        # Create widgets
        self.playerSide = PlayerSide(self.root, self)
        self.buttonSide = ButtonSide(self.root, self)

class PlayerSide(ScreenFrame):
    def __init__(self, *args, **kwargs):
        ScreenFrame.__init__(self, *args, **kwargs)
        # Create player select widgets
        self.player1Sel = PlayerSelect(self.root, self.root.players[0], self)
        self.player2Sel = PlayerSelect(self.root, self.root.players[1], self)
        self.pack()
    def pack(self):
        ScreenFrame.pack(self, side="top", fill="both", expand=True)

class PlayerSelect(ScreenFrame):
    def __init__(self, root, player: Player, *args, **kwargs):
        ScreenFrame.__init__(self, root, *args, **kwargs)
        self.title = ttk.Label(self, text=player.label, font=[None,24,'bold'])
        playerSize = 80
        self.player = tk.Canvas(
            self, width=playerSize, height=playerSize,
            bd=0, highlightthickness=0, bg=BG_COLOR
        )
        options = Player.optionList

        self.value = player.playerOption = tk.StringVar(self)
        self.value.trace('w', player.onSelect)
        self.value.set(options[0])
        self.select = ttk.Combobox(
            self, textvariable=self.value,
            values=options, state='readonly'
        )
        # Pack widgets
        self.title.pack(side="top", pady=20)
        self.player.pack(side="top", padx=20, pady=60)
        self.select.pack(fill="both", ipadx=10, ipady=5, pady=20)
        # Create circle
        self.player.create_oval(
            0, 0, playerSize, playerSize, width=0, fill=player.color
        )
        self.pack()
    def pack(self):
        ScreenFrame.pack(
            self, side="left", padx=40, pady=20,
            fill="both", expand=True
        )

class ButtonSide(ScreenFrame):
    def __init__(self, *args, **kwargs):
        ScreenFrame.__init__(self, *args, **kwargs)
        # Create widgets
        self.playButton = ttk.Button(
            self, text="Đấu", command=lambda: self.root.navigator.push(self.root.play)
        )
        # self.batchPlayButton = ttk.Button(
        #     self, text="Đấu Hàng Loạt",
        #     command=lambda: self.root.navigator.push(self.root.batch)
        # )
        self.playButton.pack(
            side="left", fill="both", expand=True, padx=20, pady=20
        )
        # self.batchPlayButton.pack(
        #     side="left", fill="both", expand=True, padx=20, pady=20
        # )
        self.pack()
    def pack(self):
        ScreenFrame.pack(self, side="top", fill="both")
