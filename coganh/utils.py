import tkinter as tk
import tkinter.ttk as ttk
from coganh.config import BOARD_SIZE, CHESS_SIZE

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

decodedBoardHelper = [[[(0, 1), (1, 1), (1, 0)],
[(0, 2), (1, 1), (0, 0)],
[(0, 3), (1, 2), (0, 1), (1, 3), (1, 1)],
[(0, 4), (1, 3), (0, 2)],
[(1, 4), (1, 3), (0, 3)]],
[[(0, 0), (1, 1), (2, 0)],
[(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)],
[(0, 2), (1, 1), (1, 3), (2, 2)],
[(0, 2), (0, 3), (0, 4), (1, 2), (1, 4), (2, 2), (2, 3), (2, 4)],
[(2, 4), (1, 3), (0, 4)]],
[[(1, 0), (2, 1), (3, 0), (1, 1), (3, 1)],
[(1, 1), (2, 0), (2, 2), (3, 1)],
[(1, 1), (1, 2), (1, 3), (2, 1), (2, 3), (3, 1), (3, 2), (3, 3)],
[(1, 3), (2, 2), (2, 4), (3, 3)],
[(3, 4), (2, 3), (1, 4), (3, 3), (1, 3)]],
[[(2, 0), (3, 1), (4, 0)],
[(2, 0), (2, 1), (2, 2), (3, 0), (3, 2), (4, 0), (4, 1), (4, 2)],
[(2, 2), (3, 1), (3, 3), (4, 2)],
[(2, 2), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 3), (4, 4)],
[(4, 4), (3, 3), (2, 4)]],
[[(3, 0), (3, 1), (4, 1)],
[(4, 0), (3, 1), (4, 2)],
[(4, 1), (3, 2), (4, 3), (3, 1), (3, 3)],
[(4, 2), (3, 3), (4, 4)],
[(4, 3), (3, 3), (3, 4)]]]

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

initialBoard = [
    [-1, -1, -1, -1, -1],
    [-1,  0,  0,  0, -1],
    [ 1,  0,  0,  0, -1],
    [ 1,  0,  0,  0,  1],
    [ 1,  1,  1,  1,  1]
]

class Screen(ttk.Frame):
    root: tk.Tk
    def __init__(self, root, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        self.root = root
    def place(self):
        ttk.Frame.place(self, in_=self.root, x=0, y=0, relwidth=1, relheight=1)
    def unplace(self):
        ttk.Frame.place_forget(self)

class ScreenFrame(ttk.Frame):
    root: tk.Tk
    def __init__(self, root, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        self.root = root

class PlayingTimeoutError(Exception):
    pass

def toLogicalPosition(x, y):
    pad = CHESS_SIZE/2 + 2
    r = CHESS_SIZE/2
    logicalX = int((x-pad+r)/(BOARD_SIZE/4))
    logicalY = int((y-pad+r)/(BOARD_SIZE/4))
    return logicalX, logicalY

def toVisualPosition(x, y):
    pad = CHESS_SIZE/2 + 2
    visualX = x*(BOARD_SIZE/4) + pad
    visualY = y*(BOARD_SIZE/4) + pad
    return visualX, visualY