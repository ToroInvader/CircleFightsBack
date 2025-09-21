#whack initial game play setting shouldn't be here but eh

# V 0.2
input("hello circle needs to fight back agaisnt some squares press enter to continue")
inputdiffculty = int(input("what diffculty do you wanna try 1-10  just type a number the lower number the harder the game (5 is recommended, 2 for rush experience)"))
inputPowerSlider = int(input("how frequent should powerups be pick 1-10 (5 is recommended i think, 4 for rush experience i think)"))
inputNumOfEnemies = int(input("how many squares to initially fight off pick any positive integer (5 is recommended, 50 for rush experience)"))
input("to move use WASD and space to dash and q,e,f to attack good luck, press enter to continue")



#built in libraries
import random
import sys
#3rd party libraries
import pygame
from pygame.locals import *
import numpy as np
#my libraries
from Rendering import *
from Physics import *
from Collision import *
from Enemy import *
from Entity import *
from Effect import *
from Global import *

pygame.init()

#region classes

#endregion

#endregion classes

#region functions




#endregion

#region window setup
width = 1200
height = 800
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Circle FIGHTS back')
#endregion window setup

#region renderSystem setup

renderSystem = RenderSystem(window, width, height, 4)
print("this one is running")
#endregion


#region constants and initial variables that we want to define
#region colours       ( R , G , B , A ) the last one is a special value used for very specific things when needed

#endregion colours


# region environment setup
staticRenderObjects = [] # these are objects that'll never ever change there position except for scrolling purpose
staticRenderObjects.append(RenderRect(-3000, height/2, 6000, 20, colours["wood"]))
staticRenderObjects.append(RenderRect(width/2, -3000, 20, 6000, colours["wood"]))
walls = []
walls.append(Entity(CollisionRect(1000, 7500), 3100, -3300, 20, colours["black"])) # right
walls.append(Entity(CollisionRect(7500, 1000), -3300, -4100, 20, colours["black"]))  # up
walls.append(Entity(CollisionRect(1000, 7500), -4100, -3300, 20, colours["black"])) # left
walls.append(Entity(CollisionRect(7500, 1000), -3300, 3100, 20, colours["black"])) # down
dragFactor = 1 # the force counteracting on object so we can have terminal velocity(models stuff like friction and air resistance)
# endregion environment setup

# region Entities setup excluding player
entities = [] #
enemies = []
effects = []
powerUps = []
# endregion Entity setup


#region game stats
playerObject = Entity(CollisionCircle(20), width / 2, height / 2, 20, colours["red"])
playerForce = 5 #determines the speed of a player
playerDragFactor = 1

playerMaxHP = 10
playerHp = playerMaxHP

playerMaxStamina = 50
playerStamina = playerMaxStamina
dashStaminaConsumption = 10
staminaRegen = 0.1

meleeDmg = 1
meleeKB = 400
meleeSpeed = 2
meleeSize = 15
swingCD = 0.6
meleeLinger = 0.6

bulletConsumption = 5
bulletDmg = 1
bulletKB = 100
bulletSpeed = 10
bulletSize = 5
bulletCD = 0.01 #
bulletLinger = 10

homingConsumption = 30
homingCD = 1
homingDmg = 1
homingKB = meleeKB
homingSpeed = meleeSpeed
homingSize = 10
homingLinger = 10

playerProjectiles = []
bulletIDs = 0

score = 0

numOfEnemies = inputNumOfEnemies
wave = 0
maxEnemyForce = 10 # the variables here determine the difficulty and difficulty should typically get higher over time
minEnemyForce = 1
minEnemyKB = 200
maxEnemyKB = 250
minEnemyHp = 1
maxEnemyHp = 1
minEnemyDmg = 1
maxEnemyDmg = 1
enemySize = 40
bigEnemySize = 50
smallEnemySize = 20
enemySizeVariance = 5
enemyLocalInvincibility = 0.25
enemyTypes = {"sizes":False, "burster":False, "spiralIn":False, "Looker":False}

enemyProjectiles = []
enemyProjectileLimit = 500 #lower this for better performance we gotta optimise this
electricFields = [] # will be in transparent render objects
IceFields = []

wallLimit = 500

difficultySlider = inputdiffculty # how fast the game ramps up in difficulty the smaller the number the faster it ramps up
powerUpSlider = inputPowerSlider # how common power ups are
                            #insert [title] card
statuses = {"staminaRegen?":0.0, "invincible":0.0, "swingCD":0.0, "stunned":0.0, "dashing":0.0, "shootCD":0.0, "homingCD":0.0, "waveDisplay":0.0}  # gonna be a timer holding onto global cooldowns like if a player is stunned and can't move i might reconfigure this into an enum

#endregion game stats

#region UI
UIsize = 50
maxHpBar = RenderCircle(width-(10+UIsize),UIsize+10,UIsize,colours["dark red"])
hpBar = RenderCircle(width-(10+UIsize),UIsize+10,UIsize*(playerHp/playerMaxHP),colours["red"])
maxStaminaBar = RenderCircle(width-(10+UIsize),3*(UIsize+10),UIsize,colours["dark green"])
staminaBar = RenderCircle(width-(10+UIsize),3*(UIsize+10),UIsize*(playerStamina/playerMaxStamina),colours["green"])

scoreText = RenderText(10,10, 1200, UIsize, colours["purple"], int(1.5*UIsize), str(score))
gameOverText = RenderText(200,300, 1200, 3*UIsize, colours["red"], int(3*UIsize), "Game Over")
WaveText = RenderText(200,300, 1200, 3*UIsize, colours["purple"], int(2*UIsize), "Wave")
waveTextState = False

UI = []
UI.append(maxHpBar)
UI.append(hpBar)
UI.append(maxStaminaBar)
UI.append(staminaBar)
UI.append(scoreText)
#endregion UI


clock = pygame.time.Clock()
running = True


#endregion constants and initial variable that we want to define



#region main game loop
while running:
    #region input detection
    #is an input active detection(important for movement and autofire)
    keys = pygame.key.get_pressed()
    if statuses["stunned"] == 0:
        if keys[K_a]:
            playerObject.physics.addForce(np.array([-playerForce, 0]))
        if keys[K_d]:
            playerObject.physics.addForce(np.array([playerForce, 0]))
        if keys[K_s]:
            playerObject.physics.addForce(np.array([0, playerForce]))
        if keys[K_w]:
            playerObject.physics.addForce(np.array([0, -playerForce]))
        if keys[K_p]:
            playerStamina -= 2 * staminaRegen
    #has input state changed(important for buttons that only need to be pressed once like pressing menu)
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and playerStamina>0 and statuses["stunned"]==0:
                if keys[K_a] or keys[K_d] or keys[K_s] or keys[K_w]:
                    playerStamina -= dashStaminaConsumption
                    statuses["staminaRegen?"] = FPS * 0.25
                    statuses["dashing"] = FPS * 0.25
                if keys[K_a]:
                    playerObject.physics.addForce(np.array([-playerForce*50, 0]))
                if keys[K_d]:
                    playerObject.physics.addForce(np.array([playerForce*50, 0]))
                if keys[K_s]:
                    playerObject.physics.addForce(np.array([0, 50*playerForce]))
                if keys[K_w]:
                    playerObject.physics.addForce(np.array([0, -playerForce*50]))
            if event.key == pygame.K_f and statuses["swingCD"] <= 0:
                playerProjectiles.append(Bullet(CollisionCircle(meleeSize), playerObject.physics.position[0], playerObject.physics.position[1], 20, meleeDmg, meleeKB,colours["orange"], meleeLinger*FPS, "m"+str(bulletIDs)))
                bulletIDs += 1
                if bulletIDs >= 100:
                    bulletIDs = 0
                statuses["swingCD"] = swingCD*FPS
                # now find the enemy with the shortest distance
                dy=99999999
                dx=99999999
                for i in enemies:
                    if((i.physics.position[0]-playerObject.physics.position[0])**2+(i.physics.position[1]-playerObject.physics.position[1])**2<(dy)**2+(dx)**2):
                        dy = (i.physics.position[1]+i.collider.height/2)-playerObject.physics.position[1]
                        dx = (i.physics.position[0]+i.collider.width/2)-playerObject.physics.position[0]
                # now normalise dy and dx
                magnitude = np.sqrt(dy**2 + dx**2)
                dy /= magnitude
                dx /= magnitude
                playerProjectiles[-1].direction = np.array([dx, dy])
            if event.key == pygame.K_e and statuses["shootCD"] <= 0 and playerStamina > 0:
                playerStamina -= bulletConsumption
                statuses["staminaRegen?"] = FPS * 0.25
                playerProjectiles.append(Bullet(CollisionCircle(bulletSize), playerObject.physics.position[0], playerObject.physics.position[1], 20, bulletDmg, bulletKB,colours["blue"], bulletLinger*FPS, "b"+str(bulletIDs)))
                bulletIDs += 1
                if bulletIDs >= 100:
                    bulletIDs = 0
                statuses["shootCD"] = bulletCD*FPS
                # now find the enemy with the shortest distance
                dy=99999999
                dx=99999999
                for i in enemies:
                    if((i.physics.position[0]-playerObject.physics.position[0])**2+(i.physics.position[1]-playerObject.physics.position[1])**2<(dy)**2+(dx)**2):
                        dy = (i.physics.position[1]+i.collider.height/2)-playerObject.physics.position[1]
                        dx = (i.physics.position[0]+i.collider.width/2)-playerObject.physics.position[0]
                # now normalise dy and dx
                magnitude = np.sqrt(dy**2 + dx**2)
                dy /= magnitude
                dx /= magnitude
                playerProjectiles[-1].direction = np.array([dx, dy])
            if event.key == pygame.K_q and statuses["homingCD"] <= 0 and playerStamina>20:
                playerStamina -= homingConsumption
                statuses["staminaRegen?"] = FPS * 1
                playerProjectiles.append(Bullet(CollisionCircle(homingSize), playerObject.physics.position[0], playerObject.physics.position[1], 20, homingDmg, homingKB,colours["yellow"], homingLinger*FPS, "h"+str(bulletIDs)))
                bulletIDs += 1
                if bulletIDs >= 100:
                    bulletIDs = 0
                statuses["homingCD"] = homingCD*FPS
                # now find the enemy with the shortest distance
                dy=99999999
                dx=99999999
                for i in enemies:
                    if((i.physics.position[0]-playerObject.physics.position[0])**2+(i.physics.position[1]-playerObject.physics.position[1])**2<(dy)**2+(dx)**2):
                        dy = (i.physics.position[1]+i.collider.height/2)-playerObject.physics.position[1]
                        dx = (i.physics.position[0]+i.collider.width/2)-playerObject.physics.position[0]
                # now normalise dy and dx
                magnitude = np.sqrt(dy**2 + dx**2)
                dy /= magnitude
                dx /= magnitude
                playerProjectiles[-1].direction = np.array([dx, dy])


        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()
    #endregion input detection

    #region processing

    #region Wave management System
    if len(enemies) == 0: # this means a new wave should start
        wave += 1
        if wave % 2 == 1 and wave > 5:
            walls = []
            walls.append(Entity(CollisionRect(1000, 7500), 3100, -3300, 20, colours["black"]))  # right
            walls.append(Entity(CollisionRect(7500, 1000), -3300, -4100, 20, colours["black"]))  # up
            walls.append(Entity(CollisionRect(1000, 7500), -4100, -3300, 20, colours["black"]))  # left
            walls.append(Entity(CollisionRect(7500, 1000), -3300, 3100, 20, colours["black"]))  # down
            for w in range(200):
                walls.append(Entity(CollisionRect(random.randint(1, 300), random.randint(1, 300)), random.randint(-3000, 3000), random.randint(-3000, 3000), 1000, colours["black"]))
        WaveText.changeText("Wave " + str(wave))
        statuses["waveDisplay"] = FPS*2
        waveTextState = True
        UI.append(WaveText)
        playerHp = playerMaxHP # restore hp
        enemyProjectiles = []
        iceFields = []
        #probability of base difficulty sliders going up we'll stick to 1 in 10 but that could be known as the difficulty slider nvm let's implement it
        if random.randint(1,difficultySlider)==1:
            maxEnemyForce += 2
            if random.randint(1,difficultySlider)==1:
                minEnemyForce += 2
        if random.randint(1,difficultySlider)==1:
            maxEnemyKB += 20
            if random.randint(1,difficultySlider)==1:
                minEnemyKB += 20
        if random.randint(1,difficultySlider*2)==1:
            maxEnemyHp += 1
            if random.randint(1,difficultySlider*2)==1:
                minEnemyHp += 1
        if random.randint(1,difficultySlider)==1:
            maxEnemyDmg += 1
            if random.randint(1,difficultySlider)==1:
                minEnemyDmg += 1
        elements = ["fire", "wind", "electric", "ice", "steel3", "earth", "null"]
        availableElements = []
        #custom element selector which could just use random.choice
        if wave>20: # every single element is deployed
            availableElements = [("fire",colours["red"]),("wind",colours["wind"]),("electric",colours["electric"]),("ice",colours["ice"]),("earth",colours["earth"]),("null",colours["grey"]), ("steel3",colours["steel"])]
        elif wave>15:
            for i in range(3):
                randElement = random.randint(1, 7)
                if randElement == 1:
                    availableElements.append(("fire", colours["red"]))
                elif randElement == 2:
                    availableElements.append(("wind", colours["wind"]))
                elif randElement == 3:
                    availableElements.append(("electric", colours["electric"]))
                elif randElement == 4:
                    availableElements.append(("ice", colours["ice"]))
                elif randElement == 5:
                    availableElements.append(("earth", colours["earth"]))
                elif randElement == 6:
                    availableElements.append(("steel3", colours["steel"]))
                else:
                    availableElements.append(("null", colours["grey"]))
        elif wave>10:
            for i in range(2):
                randElement = random.randint(1, 7)
                if randElement == 1:
                    availableElements.append(("fire", colours["red"]))
                elif randElement == 2:
                    availableElements.append(("wind", colours["wind"]))
                elif randElement == 3:
                    availableElements.append(("electric", colours["electric"]))
                elif randElement == 4:
                    availableElements.append(("ice", colours["ice"]))
                elif randElement == 5:
                    availableElements.append(("earth", colours["earth"]))
                elif randElement == 6:
                    availableElements.append(("steel3", colours["steel"]))
                else:
                    availableElements.append(("null", colours["grey"]))

        else:
            randElement = random.randint(1,7)
            if randElement==1:
                availableElements.append(("fire",colours["red"]))
            elif randElement==2:
                availableElements.append(("wind",colours["wind"]))
            elif randElement==3:
                availableElements.append(("electric",colours["electric"]))
            elif randElement==4:
                availableElements.append(("ice",colours["ice"]))
            elif randElement==5:
                availableElements.append(("earth",colours["earth"]))
            elif randElement==6:
                availableElements.append(("steel3",colours["steel"]))
            else:
                availableElements.append(("null", colours["grey"]))



        if(wave % 5==1):
            enemyTypes = {"sizes": False, "burster": False, "spiralIn": False, "Looker": False}
        if random.randint(1,3)==1:
            enemyTypes["spiralIn"] = True
        if random.randint(1,3)==1:
            enemyTypes["sizes"] = True
        if random.randint(1,3)==1:
            enemyTypes["burster"] = True
        if random.randint(1,3)==1:
            enemyTypes["Looker"] = True


        for i in range(numOfEnemies): # deploy new enemies
            AI = [Pursuer()]
            if enemyTypes["spiralIn"]:
                AI.append(SpiralIn(bool(random.getrandbits(1))))
            if enemyTypes["burster"]:
                AI.append(Burster(random.randint(1,5)*FPS, random.randint(100,150)))
            if enemyTypes["Looker"]:
                AI.append(Looker([random.randint(-700,700), random.randint(-400,400)]))
            if enemyTypes["sizes"]:
                randosize = random.randint(1,3)
                if randosize==1: # we going big
                    size = random.randint(bigEnemySize - enemySizeVariance, bigEnemySize + enemySizeVariance)
                    currentMass = 40
                    currentDmg = random.randint(minEnemyDmg, maxEnemyDmg)*2
                    currentKB = random.randint(minEnemyKB,maxEnemyKB)*2
                    currentHp  = 2*random.randint(minEnemyHp,maxEnemyHp)
                elif randosize==2: # we going small and shush IDE about grammer
                    size = random.randint(smallEnemySize - enemySizeVariance, smallEnemySize + enemySizeVariance)
                    currentMass = 10
                    currentDmg = random.randint(minEnemyDmg, maxEnemyDmg)*0.5
                    currentKB = random.randint(minEnemyKB, maxEnemyKB) * 0.5
                    currentHp  = random.randint(minEnemyHp,maxEnemyHp)*0.5
                else: # boo being normal
                    size = random.randint(enemySize - enemySizeVariance, enemySize + enemySizeVariance)
                    currentMass = 20
                    currentDmg = random.randint(minEnemyDmg, maxEnemyDmg)
                    currentKB = random.randint(minEnemyKB, maxEnemyKB)
                    currentHp  = random.randint(minEnemyHp,maxEnemyHp)
            else:
                random.randint(minEnemyDmg, maxEnemyDmg)
                size = random.randint(enemySize - enemySizeVariance, enemySize + enemySizeVariance)
                currentMass = 20
                currentKB = random.randint(minEnemyKB,maxEnemyKB)
                currentHp = 2 * random.randint(minEnemyHp, maxEnemyHp)
                currentDmg = random.randint(minEnemyDmg, maxEnemyDmg)
            currentElement = random.choice(availableElements)
            enemies.append(Enemy(random.randint(-2700,2700),random.randint(-2700,2700),size,size,currentMass,random.randint(minEnemyForce,maxEnemyForce),currentDmg,currentHp,currentKB,enemyLocalInvincibility*FPS, random.choice(AI), currentElement[0], currentElement[1]))
        numOfEnemies = int(np.ceil(numOfEnemies*1.1))
    #endregion

    #region enemy AI behaviour and adding forces
    for i in enemies:
        direction = i.AI.move(i.physics.position[0], i.physics.position[1], playerObject.physics.position[0], playerObject.physics.position[1])
        if direction[0] != 0 and direction[1] != 0:
            i.direction = direction
            i.physics.addForce(i.force*i.direction)
            i.direction /= np.linalg.norm(i.direction)
    #endregion

    #region physics manipulation and wall collision
    for i in powerUps:
        i.physics.addForce(i.physics.velocity*-dragFactor)
        physicsSystem.updatePhysics(i, i.physics)
    playerObject.physics.addForce(playerObject.physics.velocity*-playerDragFactor) # add drag force
    for i in walls:
        if not keys[K_p]:
            circleToWall(playerObject, i) #no more chaotic looking code go refer to the function anyways all it does see the behaviour of an object trying to bash into a wall
        for j in enemies:
            if not(j.element == "wind" or j.element=="earth"):
                RectToWall(j, i)

    physicsObject.updatePhysics(playerObject.physics)
    #endregion physics manipulation


    #region enemy collision logic
    for i in enemies:
        if CollisionSystem.rectInCircle(i.physics.position[0], i.physics.position[1], i.collider, playerObject.physics.position[0], playerObject.physics.position[1], playerObject.collider):
            if statuses["invincible"]==0:
                statuses["invincible"] = FPS*0.8
                playerHp -= i.dmg
                if i.element == "wind":
                    i.kb *= 1.5
                playerObject.physics.addForce(i.direction*i.kb)
    #endregion enemy collision logic

    #region enemy elemence management
    for i in enemies:
        if i.element == "fire":
            if(random.randint(1,360)==1): # how likely a fire attack can occur
                enemyProjectiles.append(Bullet(CollisionRect(max(i.collider.width/5,10),max(i.collider.width/5,10)), i.physics.position[0]+i.collider.width/2, i.physics.position[1]+i.collider.height/2, 20, i.dmg, i.kb/2, i.colour,10,"fire"))
                dy =   playerObject.physics.position[1] - (i.physics.position[1] + i.collider.height / 2)
                dx =   playerObject.physics.position[0] -(i.physics.position[0] + i.collider.width / 2)
                # now normalise dy and dx
                magnitude = np.sqrt(dy ** 2 + dx ** 2)
                dy /= magnitude
                dx /= magnitude
                enemyProjectiles[-1].direction = np.array([dx, dy])*random.randint(int(i.force/2),i.force)
        if i.element == "wind":
            if(random.randint(1,180)==1): # how likely a wind attack can occur
                enemyProjectiles.append(Bullet(CollisionRect(max(i.collider.width/5,10),max(i.collider.width/5,10)), i.physics.position[0]+i.collider.width/2, i.physics.position[1]+i.collider.height/2, 20, 0, i.kb*2, i.colour,5,"wind"))
                dy =   playerObject.physics.position[1] - (i.physics.position[1] + i.collider.height / 2)
                dx =   playerObject.physics.position[0] -(i.physics.position[0] + i.collider.width / 2)
                # now normalise dy and dx
                magnitude = np.sqrt(dy ** 2 + dx ** 2)
                dy /= magnitude
                dx /= magnitude
                enemyProjectiles[-1].direction = np.array([dx, dy])*random.randint(int(i.force/2),i.force)
        if i.element.startswith("steel"):
            if(random.randint(1,600)==1) and int(i.element[-1]) != 0: # how likely a steel summon occurs
                size = i.collider.width/2
                enemies.append(Enemy(i.physics.position[0], i.physics.position[1], size, size, i.physics.mass/2, i.force, i.dmg/2, i.hp, i.kb, enemyLocalInvincibility * FPS,i.AI, "steel0", colours["steel"]))
                enemies[-1].physics.addForce(np.array([random.uniform(-1,1),random.uniform(-1,1)*i.kb]))
                i.element = "steel"+str(int(i.element[-1])-1)

    #endregion
    #region specific elemence interactions
    electricEnemies = []
    windEnemies = []
    steelEnemies = []
    electricFields = []
    earthEnemies = []
    iceEnemies = []
    for i in enemies:
        if i.element.startswith("electric"):
            i.element = "electric"
            electricEnemies.append(i)
        elif i.element.startswith("wind"):
            windEnemies.append(i)
        elif i.element.startswith("steel"):
            steelEnemies.append(i)
        elif i.element == "earth":
            earthEnemies.append(i)
        elif i.element == "ice":
            iceEnemies.append(i)
    for i in electricEnemies:
        if i.element.endswith("charged"):
            continue
        # now find a compatible enemy with the shortest distance in a certain range
        dy = i.collider.height*5
        dx = i.collider.width*5
        latchEnemy = None
        for j in electricEnemies:
            if (i.physics.position[1] == j.physics.position[1] and i.physics.position[0] == j.physics.position[0]) or j.element.endswith("charged"):
                continue
            newdy = abs((i.physics.position[1] + i.collider.height/2) - (j.physics.position[1] + j.collider.height/2))
            newdx = abs((i.physics.position[0] + i.collider.width/2)  - (j.physics.position[0] + j.collider.width/2))
            if newdx**2+newdy**2 < dy**2+dx**2:
                dy = newdy
                dx = newdx
                latch = True
                latchCoords = [j.physics.position[0] + j.collider.width/2,j.physics.position[1] + j.collider.height/2]
                latchEnemy = j
            for j in windEnemies:
                if (i.physics.position[1] == j.physics.position[1] and i.physics.position[0] == j.physics.position[0]) or j.element.endswith("charged"):
                    continue
                newdy = abs((i.physics.position[1] + i.collider.height/2) - (j.physics.position[1] + j.collider.height/2))
                newdx = abs((i.physics.position[0] + i.collider.width/2)  - (j.physics.position[0] + j.collider.width/2))
                if newdx**2+newdy**2 < dy**2+dx**2:
                    dy = newdy
                    dx = newdx
                    latch = True
                    latchCoords = [j.physics.position[0] + j.collider.width/2,j.physics.position[1] + j.collider.height/2]
                    latchEnemy = j
            for j in steelEnemies:
                if (i.physics.position[1] == j.physics.position[1] and i.physics.position[0] == j.physics.position[0]) or j.element.endswith("charged"):
                    continue
                newdy = abs((i.physics.position[1] + i.collider.height/2) - (j.physics.position[1] + j.collider.height/2))
                newdx = abs((i.physics.position[0] + i.collider.width/2)  - (j.physics.position[0] + j.collider.width/2))
                if newdx**2+newdy**2 < dy**2+dx**2:
                    dy = newdy
                    dx = newdx
                    latch = True
                    latchCoords = [j.physics.position[0] + j.collider.width/2,j.physics.position[1] + j.collider.height/2]
                    latchEnemy = j
        if latchEnemy is not None:
            if latchEnemy.element == "wind":
                i.element = "electriccharged"
                pass
                #no field is generated if electric and wind are the closest 😈 but electric ignores the closest fire if an uncharged electric is close enough
            elif latchEnemy.element.startswith("steel"):
                i.element = "electriccharged"
                newDmg = (latchEnemy.dmg + i.dmg) / 2
                direction = np.add(i.direction, latchEnemy.direction) / 2
                newCoords = (min(i.physics.position[0] + i.collider.width / 2,latchEnemy.physics.position[0] + latchEnemy.collider.width / 2),min(i.physics.position[1] + i.collider.height / 2,latchEnemy.physics.position[1] + latchEnemy.collider.height / 2))
                electricFields.append(DmgField(newCoords[0], newCoords[1], dx, dy, 20, direction, newDmg, i.kb * 4, transparentColour(colours["electric"], 120)))

            elif latchEnemy.element == "electric":
                latchEnemy.element = "electriccharged"
                i.element = "electriccharged"
                newDmg = (latchEnemy.dmg + i.dmg)/2
                direction = np.add(i.direction , latchEnemy.direction) / 2
                newCoords = (min(i.physics.position[0] + i.collider.width/2,latchEnemy.physics.position[0] + latchEnemy.collider.width/2), min(i.physics.position[1] + i.collider.height/2,latchEnemy.physics.position[1] + latchEnemy.collider.height/2))
                electricFields.append(DmgField(newCoords[0], newCoords[1], dx, dy, 20, direction, newDmg, i.kb*4,transparentColour(colours["electric"], 120)))

    for i in earthEnemies:
        if not random.randint(1,600)==1: #the potential to make a wall
            continue
        dy = 400
        dx = 400
        latchEnemy = None
        for j in earthEnemies:
            if (i.physics.position[1] == j.physics.position[1] and i.physics.position[0] == j.physics.position[0]):
                continue
            newdy = abs(
                (i.physics.position[1] + i.collider.height / 2) - (j.physics.position[1] + j.collider.height / 2))
            newdx = abs((i.physics.position[0] + i.collider.width / 2) - (j.physics.position[0] + j.collider.width / 2))
            if newdx ** 2 + newdy ** 2 < dy ** 2 + dx ** 2:
                dy = newdy
                dx = newdx
                latch = True
                latchCoords = [j.physics.position[0] + j.collider.width / 2,
                               j.physics.position[1] + j.collider.height / 2]
                latchEnemy = j
        if latchEnemy != None:
            newCoords = (min(i.physics.position[0] + i.collider.width / 2,
                             latchEnemy.physics.position[0] + latchEnemy.collider.width / 2),
                         min(i.physics.position[1] + i.collider.height / 2,
                             latchEnemy.physics.position[1] + latchEnemy.collider.height / 2))
            walls.append(Entity(CollisionRect(dx,dy), newCoords[0], newCoords[1], i.physics.mass, colours["earth"]))
    for i in iceEnemies:
        if not random.randint(1,600)==1: #the potential to make a wall
            continue
        dy = 1000
        dx = 1000
        latchEnemy = None
        for j in iceEnemies:
            if (i.physics.position[1] == j.physics.position[1] and i.physics.position[0] == j.physics.position[0]):
                continue
            newdy = abs(
                (i.physics.position[1] + i.collider.height / 2) - (j.physics.position[1] + j.collider.height / 2))
            newdx = abs((i.physics.position[0] + i.collider.width / 2) - (j.physics.position[0] + j.collider.width / 2))
            if newdx ** 2 + newdy ** 2 < dy ** 2 + dx ** 2:
                dy = newdy
                dx = newdx
                latch = True
                latchCoords = [j.physics.position[0] + j.collider.width / 2,
                               j.physics.position[1] + j.collider.height / 2]
                latchEnemy = j
        if latchEnemy != None:
            newCoords = (min(i.physics.position[0] + i.collider.width / 2,
                             latchEnemy.physics.position[0] + latchEnemy.collider.width / 2),
                         min(i.physics.position[1] + i.collider.height / 2,
                             latchEnemy.physics.position[1] + latchEnemy.collider.height / 2))
            iceFields.append(Entity(CollisionRect(dx,dy), newCoords[0], newCoords[1], i.physics.mass, colours["icePlatform"]))

    #endregion


    #region bullet management deletion code should be separate to update code


    for i in playerProjectiles:
        i.time -= 1
        if i.id[0] == "m":
            if len(enemies) != 0:
                dy = 999999
                dx = 999999
                for j in enemies:
                    if ((j.physics.position[0] - playerObject.physics.position[0]) ** 2 + (j.physics.position[1] - playerObject.physics.position[1]) ** 2 < (dy) ** 2 + (dx) ** 2):
                        dy = (j.physics.position[1] + j.collider.height / 2) - playerObject.physics.position[1]
                        dx = (j.physics.position[0] + j.collider.width / 2) - playerObject.physics.position[0]
                # now normalise dy and dx
                magnitude = np.sqrt(dy ** 2 + dx ** 2)
                dy /= magnitude
                dx /= magnitude
                i.direction = np.array([dx, dy])
            i.relativePos = np.add(i.direction * meleeSpeed, i.relativePos)
            i.physics.position = np.add(i.relativePos, playerObject.physics.position)
        if i.id[0] == "h":
            if len(enemies) != 0:
                dy = 999999
                dx = 999999
                for j in enemies:
                    if ((j.physics.position[0] - i.physics.position[0]) ** 2 + (j.physics.position[1] - i.physics.position[1]) ** 2 < (dy) ** 2 + (dx) ** 2):
                        dy = (j.physics.position[1] + j.collider.height / 2) - i.physics.position[1]
                        dx = (j.physics.position[0] + j.collider.width / 2) - i.physics.position[0]
                # now normalise dy and dx
                magnitude = np.sqrt(dy ** 2 + dx ** 2)
                dy /= magnitude
                dx /= magnitude
                i.direction = np.array([dx, dy])
            i.physics.position = np.add(i.direction * homingSpeed, i.physics.position)
        if i.id[0] == "b":
            i.physics.position = np.add(i.direction * bulletSpeed, i.physics.position)

    for i in playerProjectiles[:]:
        if i.time <= 0:
            playerProjectiles.remove(i)

    newPlayerProjectiles = []
    for i in playerProjectiles[:]:
        remove = False
        if i.id[0] == "b" or i.id[0] == "h":
            for j in walls:
                if CollisionSystem.rectInCircle(j.physics.position[0], j.physics.position[1], j.collider, i.physics.position[0], i.physics.position[1], i.collider):
                    remove = True
                    break
            # detect enemies
        for j in enemies[:]:
            if CollisionSystem.rectInCircle(j.physics.position[0], j.physics.position[1], j.collider, i.physics.position[0], i.physics.position[1], i.collider):
                # enemy has been hit
                if not i.id in j.hits.keys():
                    if i.id[0] == "m":
                        j.hp -= i.dmg
                        j.hits[i.id] = j.localInvincibility * FPS
                        j.physics.addForce(i.direction*i.kb)
                    elif i.id[0] == "b" :
                        j.hp -= i.dmg
                        j.hits[i.id] = j.localInvincibility * FPS
                        j.physics.addForce(i.direction * i.kb)
                        remove = True
                    elif i.id[0] == "h" :
                        j.hp -= i.dmg
                        j.hits[i.id] = j.localInvincibility * FPS
                        j.physics.addForce(i.direction * i.kb)
                        remove = True
        if not remove:
            newPlayerProjectiles.append(i)
    playerProjectiles = newPlayerProjectiles

    for i in enemyProjectiles:
        i.physics.position = np.add(i.direction, i.physics.position)

    # fire and wind interaction
    wind_projectiles = []
    fire_projectiles = []
    great_projectiles = []
    basic_projectiles = []
    for p in enemyProjectiles:
        if p.id == "wind":
            wind_projectiles.append(p)
        elif p.id == "fire":
            fire_projectiles.append(p)
        else:
            basic_projectiles.append(p)

    for i in fire_projectiles: # electric and fire interaction
        for j in electricFields:
            if CollisionSystem.rectInRect(i.physics.position[0], i.physics.position[1], i.collider, j.physics.position[0], j.physics.position[1], j.collider):
                i.direction *= 1.2 # we will let them projectiles accelerate in the field

    for i in wind_projectiles[:]:
        remove = False
        for j in fire_projectiles[:]:
            if CollisionSystem.rectInRect(i.physics.position[0], i.physics.position[1], i.collider, j.physics.position[0], j.physics.position[1], j.collider):
                # fire and wind interaction when there bullets collide giga flame bullet is spawned in
                newDirection = np.add(i.direction, j.direction)
                newDirection /= 4
                great_projectiles.append(Bullet(CollisionRect(i.collider.width * 15, i.collider.height * 15), i.physics.position[0], i.physics.position[1],20, j.dmg * 2, i.kb * 2, colours["flame"], 10, "greatFlame"))
                great_projectiles[-1].direction = newDirection
                remove=True
                fire_projectiles.remove(j)
                break
        if remove:
            wind_projectiles.remove(i)
    enemyProjectiles = fire_projectiles + wind_projectiles + great_projectiles + basic_projectiles



    for i in enemyProjectiles[:]:
        remove = False
        if CollisionSystem.rectInCircle(i.physics.position[0], i.physics.position[1], i.collider, playerObject.physics.position[0], playerObject.physics.position[1], playerObject.collider):
            if statuses["invincible"]==0:
                statuses["invincible"] = FPS*0.8
                playerHp -= i.dmg
                kbDirection = i.direction / max(1,np.linalg.norm(i.direction))
                playerObject.physics.addForce(kbDirection*i.kb)
                remove = True
        for j in walls:
            if CollisionSystem.rectInRect(i.physics.position[0], i.physics.position[1], i.collider, j.physics.position[0], j.physics.position[1], j.collider):
                remove = True
        if i.id != "greatFlame":
            for j in playerProjectiles:
                if j.id[0] == "m" and CollisionSystem.rectInCircle(i.physics.position[0], i.physics.position[1], i.collider, j.physics.position[0], j.physics.position[1], j.collider):
                    remove = True
        if remove:
            enemyProjectiles.remove(i)

    # curb enemy projectile amount and wall amount(so player don't get stuck somewhere)
    if len(enemyProjectiles) >= enemyProjectileLimit:
        for i in range(len(enemyProjectiles)-enemyProjectileLimit):
            del enemyProjectiles[0]
    if len(walls) >= wallLimit:
        for i in range(len(walls)-wallLimit):
            del walls[4]

    #endregion bullet management

    #field management, psst electric enemies are the only ones that have this property..... this ain't true anymore ice also have fields
    for i in electricFields:
        if CollisionSystem.rectInCircle(i.physics.position[0], i.physics.position[1], i.collider, playerObject.physics.position[0], playerObject.physics.position[1], playerObject.collider):
            if statuses["invincible"]==0:
                statuses["invincible"] = FPS*0.8
                statuses["stunned"] = FPS*1.6
                playerHp -= i.dmg
                playerObject.physics.addForce(i.direction*i.kb)

    playerDragFactor = 1
    for i in iceFields:
        if CollisionSystem.rectInCircle(i.physics.position[0], i.physics.position[1], i.collider, playerObject.physics.position[0], playerObject.physics.position[1], playerObject.collider):
            playerDragFactor = 0

    # enemy management
    for i in enemies[:]:
        if i.hp <= 0:
            # The enemy has died also this will be only spot to customise death effects
            numOfEffects = random.randint(3, 10)
            for e in range(numOfEffects):
                randSize = random.randint(1, 10)
                effects.append(Effect(CollisionRect(randSize, randSize), i.physics.position[0], i.physics.position[1], 20, i.colour, FPS * random.uniform(0.1, 0.5), 1,[random.uniform(-5, 5), random.uniform(-5, 5)], True))

            #generate a powerup if can happen
            if random.randint(1,powerUpSlider)==1:
                Atype = random.choice([("homing",colours["yellow"]), ("bullet",colours["blue"]), ("melee",colours["orange"]), ("stamina",colours["green"]), ("health",colours["red"])])
                powerUps.append(PowerUP(CollisionCircle(20), i.physics.position[0], i.physics.position[1], 20, Atype[1], Atype[0]))
                powerUps[-1].physics.addForce(np.array([random.uniform(-1,1),random.uniform(-1,1)])*200)


            enemies.remove(i)
            score += 10
        for k in i.hits.copy():
            i.hits[k] -= 1
            if i.hits[k] <= 0:
                del i.hits[k]


    # powerup management and two seperate loops cuase i don't wanna deal with double deletetion
    for i in powerUps[:]:
        if CollisionSystem.circleInCircle(i.physics.position[0], i.physics.position[1], i.collider, playerObject.physics.position[0], playerObject.physics.position[1], playerObject.collider):
            # the objects have collided
            for a in range(random.randint(1,10)):
                randSize = random.randint(1, 5)
                effects.append(Effect(CollisionCircle(randSize), i.physics.position[0], i.physics.position[1], 20, i.colour,FPS * random.uniform(0.1, 0.5), 1, [random.uniform(-5, 5), random.uniform(-5, 5)], True))
            #apply the effect the powerup needs to dish out
            if i.type=="health":
                if random.randint(1,2)==1:
                    playerMaxHP += 2
                else:
                    playerForce += 0.5
                playerHp = playerMaxHP
            if i.type == "stamina":
                if random.randint(1,2)==1:
                    playerMaxStamina += 20
                else:
                    staminaRegen += 0.01
                playerStamina = playerMaxStamina
            if i.type == "melee":
                randUpgrade = random.randint(1,10)
                if  1 <= randUpgrade <= 3:
                    meleeDmg += 1
                elif 4 <=  randUpgrade <= 6:
                    meleeSpeed += 0.5
                elif 10 <= randUpgrade <= 10:
                    if swingCD <= 0.11:
                        meleeDmg += 1
                        meleeSpeed += 0.5
                        meleeKB += 40
                        playerStamina = -1
                    else:
                        swingCD -= 0.1
                        meleeLinger -= 0.1
                elif 7 <= randUpgrade <= 9:
                    meleeKB += 40
            if i.type == "bullet":
                randUpgrade = random.randint(1,9)
                if  1 <= randUpgrade <= 3:
                    bulletDmg += 1
                elif 4 <=  randUpgrade <= 6:
                    bulletSpeed += 2
                elif 7 <= randUpgrade <= 9:
                    bulletKB += 10
            if i.type == "homing":
                randUpgrade = random.randint(1,9)
                if  1 <= randUpgrade <= 3:
                    homingDmg += 1
                elif 4 <=  randUpgrade <= 6:
                    homingSpeed +=0.5
                elif 7 <= randUpgrade <= 9:
                    homingKB += 40
            powerUps.remove(i)

    for i in powerUps[:]:
        i.time -= 1
        if i.time < 0:
            powerUps.remove(i)

    #region effect processing
    for i in effects[:]:
        i.time -= i.timeDecrease
        if i.fade:
            i.colour = transparentColour((i.colour[0],i.colour[1],i.colour[2]),(i.time/i.totalTime)*255)
        i.physics.position[0] += i.velocity[0]
        i.physics.position[1] += i.velocity[1]
        if i.time <= 0:
            effects.remove(i)

    #endregion effect processing

    #region game processing
    if playerStamina < 0:
        playerStamina=0
        statuses["staminaRegen?"] = FPS*3

    if playerStamina < playerMaxStamina and statuses["staminaRegen?"]==0:
        playerStamina += staminaRegen

    if statuses["dashing"]!=0:
        if statuses["dashing"]%3 == 0:
            effects.append(Effect(CollisionCircle(playerObject.collider.r),playerObject.physics.position[0],playerObject.physics.position[1],20,transparentColour(colours["red"],120),10,1,(0,0),True))

    if playerHp <= 0:
        running = False

    for k in statuses:
        if statuses[k]>0:
            statuses[k] -= 1
    #endregion

    #region update UI elements
    staminaBar.r = UIsize*playerStamina/playerMaxStamina
    hpBar.r = UIsize*playerHp/playerMaxHP
    scoreText.changeText(str(score))
    #endregion update UI elements
    #endregion processing

    #region Rendering Section
    if statuses["stunned"]!=0: # probably not the right place to implement this but it's a visual issue
        offsetX = random.randint(-3,3)
        offsetY = random.randint(-3,3)
    else:
        offsetX = 0
        offsetY = 0
    if statuses["waveDisplay"] == 0 and waveTextState:
        waveTextState=False
        UI.remove(WaveText)
    # if someone knows how to mass add lists let me know cause uhh yeah
    #jokes on you figured it out 😈 (uhh chatgpt suggested it)
    """note always draw the background first then move your way to the foreground or just assign them the correct layer number(code runs faster if you do numbers in order)"""
    render_batches =  [[staticRenderObjects, True, 0],
                       [iceFields, True, 0],
                       [walls, True, 0],
                       [enemies, True, 0],
                       [playerProjectiles,True,0],
                       [enemyProjectiles,True,0],
                       [powerUps, True, 0],
                       [[RenderCircle((width/2)+offsetX, (height/2)+offsetY, 20, colours["red"])], False, 0], # this is our player sprite can customise our player sprite later on by making them their own list
                       [electricFields,True,1],
                       [effects, True, 1],
                       [UI, False, 2]]
    renderSystem.drawScreen(render_batches, playerObject.physics.position[0] - (width / 2), playerObject.physics.position[1] - (height / 2))
    pygame.display.flip()
    clock.tick(FPS)
    #endregion Rendering Section
#endregion main game loop

#region endgame aftermath
UI.append(gameOverText)

renderSystem.drawScreen(render_batches, playerObject.physics.position[0] - (width / 2), playerObject.physics.position[1] - (height / 2))
pygame.display.flip()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


#endregion endgame aftermath