from typing import List
from coganh.utils import Screen

class Navigator:
    def __init__(self) -> None:
        self.stack: List[Screen] = []
    def push(self, screen: Screen):
        if len(self.stack) > 0:
            self.stack[-1].unplace()
        self.stack.append(screen)
        self.stack[-1].place()
    def pop(self):
        if len(self.stack) > 0:
            self.stack[-1].unplace()
            if len(self.stack) > 1:
                self.stack.pop()
            self.stack[-1].place()