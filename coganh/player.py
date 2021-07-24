from typing import Tuple
from coganh.players import __all__ as optionList
from coganh.players import *
import tkinter as tk
import threading

class Player:
    name: str
    label: str
    color: str
    isClicked: threading.Event
    outputPos: Tuple[Tuple]
    playerOption: tk.StringVar
    optionList = ["Người"] + [x+" (Máy)" for x in optionList]
    step = 0
    playerList = []
    def __init__(self, id, label, color):
        self.id = id
        self.label = label
        self.color = color
        self.isClicked = threading.Event()
        self.outputPos = None
        self.next = None
        Player.playerList.append(self)
        # print(optionList)

    def isMan(self):
        return Player.optionList.index(self.name) == 0

    def onSelect(self, index, value, mode):
        self.name = self.playerOption.get()
        # print(f'{index},{value},{mode}: {self.name}')
        # print(Player.optionList.index(self.name))
        if self.isMan():
            self.move = self.defaultMove
        else:
            i = Player.optionList.index(self.name)
            self.move = eval(optionList[i-1]).move

    def defaultMove(self, board, player):
        self.isClicked.clear()
        self.isWaiting = True
        self.outputPos = None
        self.isClicked.wait()
        return self.outputPos

    def move(self, board, player):
        pass

    @classmethod
    def connect(cls):
        cls.playerList[0].next = cls.playerList[1]
        cls.playerList[1].next = cls.playerList[0]
        return [cls.playerList[0], cls.playerList[1]]

    @classmethod
    def next(cls):
        index = (cls.step)%2
        cls.step += 1
        return cls.playerList[index]
    @classmethod
    def prev(cls):
        index = (cls.step)%2
        cls.step -= 1
        return cls.playerList[index]

    @classmethod
    def reset(cls):
        cls.step = 0
