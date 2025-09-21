"""goes hand in hand with collision specifically handles broad phase collision while
the actual collision file handles narrow phase collision
note this is just a data structure
"""
from collections import  defaultdict
import math

class SpatialHashGrid:
    def __init__(self, cell_size=64):
        self.cell_size = cell_size
        self.cells = defaultdict(set) #maps (cell posx, cell posy) -> to set of entity IDS

    def cell_coords(self, x, y): #convert world coords to cell coords
        return (int(x // self.cell_size), int(y // self.cell_size))

    def insert(self, eid, x, y, width=0, height=0): #presume x,y is the centre and width and height is bounding box information that a  collision shape enroaches
        """"insert an entity into one or more cells"""
        min_x, min_y = self.cell_coords(x-(width/2),y-(height/2))
        max_x, max_y = self.cell_coords(x + (width / 2), y + (height / 2))
        for cx in range(min_x, max_x+1):
            for cy in range(min_y, max_y+1):
                self.cells[(cx, cy)].add(eid)

    def query_neighbours(self, x, y, width=0, height=0):
        candidates = set()
        min_x, min_y = self.cell_coords(x-(width/2),y-(height/2))
        max_x, max_y = self.cell_coords(x + (width / 2), y + (height / 2))
        for cx in range(min_x, max_x+1):
            for cy in range(min_y, max_y+1):
                candidates = candidates | self.cells.get((cx,cy), set())
        return candidates

    def clear(self):
        self.cells.clear()
