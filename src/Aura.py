"""The thing this piece of code is just emenate an effect at intervals"""
from turtledemo.chaos import coosys

from fontTools.merge import timer

from ECS import *
from Global import *
from Effect import *

class AuraComponent(Component):

    def __init__(self, duration, interval, auraSpan,colour=None): # interval is how many should it take to be produced
        super().__init__("aura")
        self.duration = duration*FPS
        self.auraSpan = auraSpan
        self.interval = interval
        self.colour = colour
        self.elapsed = 0



class AuraSystem:

    def tick(self, ecs: ECS):
        eids = ecs.query("aura", "render", "position")
        for id in eids:
            aura = ecs.get_component(id, "aura")
            render = ecs.get_component(id, "render")
            position = ecs.get_component(id, "position")
            if aura.colour == None:
                colour = render.colour
            else:
                colour = aura.colour
            if aura.elapsed % aura.interval == 0:
                if render.renderType == "circle":
                    createEffect(ecs, position.position[0], position.position[1], render.r, "circle", colour,0, 0, aura.auraSpan, True)
                elif render.renderType == "rect":
                    createEffect(ecs, position.position[0], position.position[1], [render.width, render.height], "rect", colour,0, 0, aura.auraSpan, True)
                elif render.renderType == "polygon":
                    createEffect(ecs, position.position[0], position.position[1], render.points, "polygon", colour,0, 0, aura.auraSpan, True)
            aura.elapsed +=1
            if aura.elapsed >= aura.duration:
                #since it's the last one nothing bad should happen
                ecs.remove_component(id, "aura")