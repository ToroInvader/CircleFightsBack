#built in library

#3rd party library
import pygame
#my libraries
from Global import  *
from ECS import *
import Vector


class RenderComponent(Component):

    def __init__(self, renderType, colour, isScroll=False, layer=0):
        """quick rant circles need x,y to be center of themselves that is how they're
        drawn while x,y of rects is now the center to accommodate for physics also remember y increases downwards"""
        super().__init__("render")
        self.colour = colour
        self.renderType = renderType #what type of object we're drawing
        self.renderX = 0.0
        self.renderY = 0.0
        self.isScroll = isScroll
        self.layer = layer

class RenderCircle(RenderComponent):

    def __init__(self, r, colour, isScroll=False, layer=0):
        super().__init__("circle", colour, isScroll, layer)
        self.r = r

class RenderRect(RenderComponent):

    def __init__(self, width, height, colour, isScroll=False, layer=0):
        super().__init__("rect", colour, isScroll, layer)
        self.height = height
        self.width = width

class RenderText(RenderRect):
    def __init__(self,width,height,colour,size,text, isScroll=False, layer=0):
        super().__init__(width, height, colour, isScroll, layer)
        self.font = pygame.font.Font('freesansbold.ttf', size)
        self.renderType = "text"
        self.trueText = text
        self.text =  self.font.render(text, True, colour)

    def changeText(self, text):
        self.trueText = text
        self.text = self.font.render(text, True, self.colour)

class RenderPolygon(RenderComponent):

    def __init__(self, points, colour, isScroll=False, layer=0): # the set of coordinates indicate the points of the triangle
        super().__init__("polygon", colour, isScroll, layer)
        self.points = Vector.forceCounterClockwise(points)

#renderSystem is starting to not be a static class
class RenderSystem:

    def __init__(self, window, width, height, layerCount, scroll_offset, bg_colour=colours["white"]):
        self.window = window
        self.width = width
        self.height = height
        self.bg_colour = bg_colour
        self.scroll_offset = scroll_offset
        self.layers = []
        for i in range(layerCount):
            self.layers.append(pygame.Surface((width, height), pygame.SRCALPHA))

    def tick(self, ecs: ECS, scroll_offset):
        self.scroll_offset = scroll_offset #render needs to know where to scroll at all times
        eids = ecs.query("position", "render") #position is obviously needed to know where to render
        self.refreshScreen()
        for id in eids:
            position = ecs.get_component(id, "position")
            render = ecs.get_component(id, "render")
            if render.isScroll:
                self.scroll(render, position)
                self.render(self.layers[render.layer],render)
            else:
                render.renderX = position.position[0]
                render.renderY = position.position[1] #due to the way code was made i need to do this cause render only works with renderX property
                self.render(self.layers[render.layer],render)
        for layer in self.layers:
            self.window.blit(layer, (0,0))

    def render(self, surface, render):
        if render.renderType == "circle":
            pygame.draw.circle(surface, render.colour, (render.renderX, render.renderY), render.r)
        if render.renderType == "rect":
            pygame.draw.rect(surface, render.colour, pygame.Rect(render.renderX-render.width/2, render.renderY-render.height/2, render.width, render.height))
        if render.renderType == "polygon":
            rendered = []
            for i in range(len(render.points)):
                rendered.append(Vector.Add(render.points[i], [render.renderX, render.renderY]))
            pygame.draw.polygon(surface, render.colour, rendered)
        if render.renderType == "text":
            surface.blit(render.text, pygame.Rect(render.renderX, render.renderY, render.width, render.height))

    def scroll(self, r, p): #r is render and p is position:
        """ this function updates one render object to be in the correct place if they treat x and y position
        to be middle of screen. Basically just implements scrolling. The r here stands for a render object. For no scrolling just make x and y 0
        """
        r.renderX = p.position[0] - self.scroll_offset[0] + self.width/2 #width and height are there to ensure centering
        r.renderY = p.position[1] - self.scroll_offset[1] + self.height/2

    def refreshScreen(self):
        for layer in self.layers:
            layer.fill((0,0,0,0))
        self.window.fill(self.bg_colour)