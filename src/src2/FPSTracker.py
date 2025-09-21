from Rendering import *
from Physics import  Position


class FPSTracker(Component):
    def __init__(self):
        super().__init__("fpstracker")

class FPSTrackerSystem:

    def deployFPSText(self, ecs: ECS):
        eid = ecs.create_entity()
        ecs.add_component(eid, RenderText(100, 100, colours["black"], 20, "FPS:", False, 2))
        ecs.add_component(eid, Position(0, 0))
        ecs.add_component(eid, FPSTracker())

    def tick(self, ecs: ECS, clock):
        eid = next(iter(ecs.query("fpstracker")))
        render: RenderText = ecs.get_component(eid, "render")
        currFPS = clock.get_fps()
        render.changeText(render.trueText[:4] + str(currFPS))