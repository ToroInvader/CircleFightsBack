from cgitb import handler

from ECS import *
from Global import *

class Timer(Component):

    def __init__(self): #duration will be in seconds
        super().__init__("timer")
        self.active = []  # list of (duration, elapsed, tag)

    def add(self, duration, tag=None):
        self.active.append([duration*60, 0, tag])

    def remove_by_tag(self, tag):
        self.active = [t for t in self.active if t[2] != tag]


class TimerSystem():
    def tick(self, ecs: ECS):
        eids = ecs.query("timer")
        for id in eids:
            timer = ecs.get_component(id, "timer")
            for t in timer.active:
                t[1] += 1
                if t[1] >= t[0]:
                    timer.remove_by_tag(t[2])