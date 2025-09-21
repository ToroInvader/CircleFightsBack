import sys
import pygame
from pygame.locals import *
from ECS import *
import Vector

class InputComponent(Component): #specialised for this game only

    def __init__(self):
        super().__init__("input")
        self.inputDir = [0,0]
        self.canDash = False
        self.canShoot = False



class InputSystem:

    def tick(self, ecs):
        eid = next(iter(ecs.query("input")))
        inputComp = ecs.get_component(eid, "input")
        self.reset(inputComp)
        #region key hit once inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT: #quit can genuinely happen here
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    inputComp.canDash = True
                elif event.key == pygame.K_f:
                    inputComp.canShoot = True
        #endregion
        #region key held inputs
        keys = pygame.key.get_pressed()
        if keys[K_d] or keys[K_RIGHT]:
            inputComp.inputDir[0] += 1
        if keys[K_a] or keys[K_LEFT]:
            inputComp.inputDir[0] -= 1
        if keys[K_s] or keys[K_DOWN]:
            inputComp.inputDir[1] += 1
        if keys[K_w] or keys[K_UP]:
            inputComp.inputDir[1] -= 1
        #endregion
        inputComp.inputDir = Vector.Unit(inputComp.inputDir) #diagonals ain't fast anymore 😈

    def reset(self, inputComp):
        inputComp.inputDir =[0,0]
        inputComp.canDash = False
        inputComp.canShoot = False