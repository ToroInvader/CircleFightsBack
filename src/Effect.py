from numpy.f2py.rules import defmod_rules

from ECS import *
from Entity import  *
from Global import *
from Rendering import *
#components
class Effect(Component): # used to make fancy effects that's it

    def __init__(self, duration ,fade): #collider is just here for shape information not to detect collisions
        super().__init__("effect")
        self.duration =  duration*FPS
        self.elapsed = 0
        self.fade = fade # boolean to say if value should fade


class EffectSystem:

    def tick(self, ecs:ECS):
        eids = ecs.query("effect", "render")
        for id in eids:
            effect = ecs.get_component(id, "effect")
            render = ecs.get_component(id, "render")
            effect.elapsed += 1 # adjust the timer
            if effect.fade:
                render.colour = transparentColour((render.colour[0],render.colour[1],render.colour[2]), ((effect.duration-effect.elapsed)/effect.duration)*255)
            if effect.elapsed >= effect.duration:
                # give the entity the death mark
                ecs.add_component(id, Remove())

def createEffect(ecs, x, y, shape, shapeTag, colour, vx, vy, duration, fade):
    eid = ecs.create_entity()
    ecs.add_component(eid, Effect(duration, fade))
    ecs.add_component(eid, Position(x,y))
    ecs.add_component(eid, Velocity(vx, vy))
    if shapeTag=="circle":
        ecs.add_component(eid, RenderCircle(shape,  colour, True, 1))
    elif shapeTag =="rect":
        ecs.add_component(eid, RenderRect(shape[0], shape[1], colour, True, 1))
    elif shapeTag=="polygon":
        ecs.add_component(eid, RenderPolygon(shape, colour, True, 1))
