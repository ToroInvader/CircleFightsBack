"""The thing this piece of code is just emenate an effect at intervals"""
from fontTools.merge import timer

from ECS import *


class AuraComponent(Component):

    def __init__(self, ecs: ECS ,duration, interval): # interval is how many should it take to be produced
        super().__init__("aura")