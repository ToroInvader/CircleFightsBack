

from ECS import *
from Entity import  *
from Global import *
from Timer import *
from Rendering import *
#components
class Effect(Component): # used to make fancy effects that's it

    def __init__(self, fade): #collider is just here for shape information not to detect collisions
        super().__init__("effect")
        self.fade = fade # boolean to say if value should fade


class EffectSystem:

    def tick(self, ecs:ECS):
        eids = ecs.query("effect", "render", "timer")
        for id in eids:
            timer = ecs.get_component(id, "timer")
            effect = ecs.get_component(id, "effect")
            render = ecs.get_component(id, "render")
            #find the effect timer
            effectTimer = None
            for t in timer.active:
                if t[2] == "effect":
                    effectTimer = t # mental note (duration, elapsed, tag) might just be better for it to be an object
            if effect.fade:
                render.colour = transparentColour((render.colour[0],render.colour[1],render.colour[2]),((effectTimer[0]-effectTimer[1])/effectTimer[0])*255)
            if effectTimer[1] >= effectTimer[0]-10:
                # give the entity the death mark
                ecs.add_component(id, Remove())


def createEffect(ecs: ECS, x, y, shape, shapeTag, colour, vx, vy, duration, fade):
    eid = ecs.create_entity()
    ecs.add_component(eid, Effect(fade))
    ecs.add_component(eid, Position(x,y))
    ecs.add_component(eid, Velocity(vx, vy))
    if shapeTag=="circle":
        ecs.add_component(eid, RenderCircle(shape,  colour, True, 1))
    elif shapeTag =="rect":
        ecs.add_component(eid, RenderRect(shape, colour, True, 1))
    elif shapeTag=="polygon":
        ecs.add_component(eid, RenderPolygon(shape, colour, True, 1))
    ecs.add_component(eid, Timer())
    timer = ecs.get_component(eid, "timer")
    timer.add(duration, "effect")
