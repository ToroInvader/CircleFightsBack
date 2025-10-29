#this is going to be used to test code that is going to be implemented

import random
from random import randint

import pygame
from pygame.locals import *
from Physics import *

pygame.init()
from ECS import *
from Collision import *
from Rendering import *
from Global import *
from FPSTracker import *
from Player import *
from Input import *
from CollisionResolvement import *
from Damage import *
from Health import *
from Enemy import *
from UI import *
from Stamina import *



clock = pygame.time.Clock()

def spawnRect(ecs: ECS):
    eid = ecs.create_entity()
    width = random.randint(1,500)
    height = random.randint(1,500)
    mass = random.randint(20,100)
    ecs.add_component(eid, CollisionRect(width, height))
    ecs.add_component(eid, RenderRect(width, height, colours["black"], True, 0))
    ecs.add_component(eid, Position(random.randint(-3000, 3000), random.randint(-3000, 3000)))
    #ecs.add_component(eid, Velocity(-1, 1))
    #ecs.add_component(eid, Physics(mass))
    ecs.add_component(eid, MotorForce(random.randint(1,10)))
    ecs.add_component(eid, StaticBody())
    ecs.add_component(eid, Material(0))


def spawnCircle(ecs: ECS):
    eid = ecs.create_entity()
    mass = random.randint(1,100)
    size = mass
    ecs.add_component(eid, CollisionCircle(size))
    ecs.add_component(eid, RenderCircle(size , colours["black"], True, 0))
    ecs.add_component(eid, Position(random.randint(-3000, 3000), random.randint(-1500, 1500)))
    ecs.add_component(eid, MotorForce(random.randint(1,10)))
    ecs.add_component(eid, StaticBody())
    ecs.add_component(eid, Material(0))

def spawnTriangle(ecs: ECS):
    eid = ecs.create_entity()
    points = []
    for i in range(3):
        point = [random.randint(-100,100), random.randint(-100,100)]
        while point in points:
            point = [random.randint(-100,100), random.randint(-100,100)]
        points.append(point)
    ecs.add_component(eid, CollisionPolygon(points))
    ecs.add_component(eid, RenderPolygon(points, colours["orange"], True, 0))
    ecs.add_component(eid, Position(random.randint(-3000, 3000), random.randint(-1500, 1500)))
    ecs.add_component(eid, Physics(20))
    ecs.add_component(eid, MotorForce(random.randint(1,10)))
    ecs.add_component(eid, StaticBody())
    ecs.add_component(eid, Material(0))


def simpleRandomiserSystem(ecs: ECS, physics: PhysicsSystem):
    eids = ecs.query("physics", "motorforce")
    for id in eids:
        component = ecs.get_component(id, "physics")
        motor = ecs.get_component(id, "motorforce")
        component.forces.append([random.randint(-motor.strength,motor.strength),0])

def CollisionCollector(ecs: ECS, events):
    for event in events["exit"]:
        if ecs.has_component(event[0], "render") and ecs.has_component(event[1], "render"):
            render1 = ecs.get_component(event[0], "render")
            render1.colour = colours["blue"]
    for event in events["enter"]:
        if ecs.has_component(event[0], "render") and ecs.has_component(event[1], "render"):
            render1 = ecs.get_component(event[0], "render")
            render1.colour = colours["green"]
    for event in events["stay"]:
        if ecs.has_component(event[0], "render") and ecs.has_component(event[1], "render"):
            render1 = ecs.get_component(event[0], "render")
            render1.colour = colours["green"]



def main():
    # region window setup
    width = 1200
    height = 800
    renderCenter = [0,0] #to force rendering to align physics position's 0
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption('test')
    # endregion

    # region ECS setup get all our systems active
    ecs = ECS()
    remover_system = RemoverSystem()
    input_system = InputSystem()
    render_system = RenderSystem(window, width, height, 4, renderCenter, colours["white"])
    collision_system = CollisionSystem(100)
    collision_resolvement_system = CollisionResolvementSystem()
    damage_system = DamageSystem()
    pursuer_system = PursuerSystem()
    straight_pursuer_system = StraightPursuerSystem()
    spiral_in_system = SpiralInSystem()
    burster_system = BursterSystem()
    looker_system = LookerSystem()
    teleporter_system = TeleporterSystem()
    physics_system = PhysicsSystem(ecs, drag=1)
    player_system = PlayerSystem()
    stamina_system = StaminaSystem()
    fps_tracker_system = FPSTrackerSystem()
    ui_system = UISystem()
    aura_system = AuraSystem()
    effect_system = EffectSystem()
    # endregion

    for i in range(0):
         spawnRect(ecs)
    for i in range(0):
       spawnEnemy(ecs, random.randint(-3000,3000), random.randint(-3000,3000), 20, 20, 20, 1, 100, 1, "teleporter", colours["grey"])
    for i in range(1000):
        spawnCircle(ecs)
    for i in range (0):
        spawnTriangle(ecs)
    spawnUI(ecs, width, height, 50)
    spawnPlayer(ecs)

    fps_tracker_system.deployFPSText(ecs)
    while True:
        input_system.tick(ecs)
        events = collision_system.tick(ecs)
        player_system.tick(ecs)
        stamina_system.tick(ecs)
        #region enemy movement
        pursuer_system.tick(ecs)
        straight_pursuer_system.tick(ecs)
        spiral_in_system.tick(ecs)
        burster_system.tick(ecs)
        looker_system.tick(ecs)
        teleporter_system.tick(ecs)
        #endregion
        collision_resolvement_system.tick(ecs, events)
        damage_system.tick(ecs, events)
        physics_system.tick(ecs)
        #region rendering things, thees are things that matter to rendering only
        position = player_system.getPlayerPos(ecs)
        fps_tracker_system.tick(ecs, clock)
        aura_system.tick(ecs)
        effect_system.tick(ecs)
        ui_system.tick(ecs)
        render_system.tick(ecs, position)
        #endregion
        remover_system.tick(ecs)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()

