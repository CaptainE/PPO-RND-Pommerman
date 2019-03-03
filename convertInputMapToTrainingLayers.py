import numpy as np

import torch
import torch.nn as nn
import torch.optim as optim
from torch.autograd import Variable
import torch.nn.functional as F
from torch.distributions import Normal

def createLayerFriendsAndEnemies(state):
    posX = state["position"][0]
    posY = state["position"][1]
    board = state["board"]
    enemies = [enemie._value_ for enemie in state["enemies"]]
    friends = state["teammate"]._value_
    layer = []
    for i, x in enumerate(range(posX - 4, posX + 5)):
        tempArr = []
        for j, y in enumerate(range(posY - 4, posY + 5)):
            if x < 0 or y < 0 or x >= 11 or y >= 11:
                tempArr.append(0) # no go out of bounce
            elif board[x][y] in enemies:
                tempArr.append(1) # enemie 
            elif board[x][y] == friends:
                tempArr.append(-1) # friend
            else:
                tempArr.append(0) # free to go here
        layer.append(tempArr)
    return layer

def createLayerDangerMap(state):
    posX = state["position"][0]
    posY = state["position"][1]
    board = state["board"]
    bombLife = state["bomb_life"]
    bombBlast = state["bomb_blast_strength"]
    layer = []
    bombs = []
    for i, x in enumerate(range(posX - 4, posX + 5)):
        tempArr = []
        for j, y in enumerate(range(posY - 4, posY + 5)):
            if x < 0 or y < 0 or x >= 11 or y >= 11:
                tempArr.append(0) # no go out of bounce
            elif board[x][y] == 4:
                tempArr.append(1) # fire 
            elif board[x][y] == 3:
                bombs.append([i, j, bombLife[x][y], bombBlast[x][y]])
                tempArr.append(0)
            else:
                tempArr.append(0) # free to go here
        layer.append(tempArr)
    for bomb in bombs:
        x = bomb[0]
        y = bomb[1]
        life = bomb[2]
        blast = int(bomb[3]) - 1
        for delta in range(-blast, blast + 1):
            xx = min(8, max(0, delta + x))
            yy = min(8, max(0, delta + y))
            layer[xx][y] = (1 - life / 11.0) ** .2
            layer[x][yy] = (1 - life / 11.0) ** .2
    
    return layer

def createLayerBoxes(state):
    posX = state["position"][0]
    posY = state["position"][1]
    board = state["board"]
    layer = []
    for x in range(posX - 4, posX + 5):
        tempArr = []
        for y in range(posY - 4, posY + 5):
            if x < 0 or y < 0 or x >= 11 or y >= 11:
                tempArr.append(0) # no go out of bounce
            elif board[x][y] == 2:
                tempArr.append(1) # box here
            else:
                tempArr.append(0) # free to go here
        layer.append(tempArr)
    layer[4][4] = 0 ## we are here !
    
    return layer

def canKickMap(state):
    posX = state["position"][0]
    posY = state["position"][1]
    board = state["board"]
    layer = []
    for x in range(posX - 4, posX + 5):
        tempArr = []
        for y in range(posY - 4, posY + 5):
            if x < 0 or y < 0 or x >= 11 or y >= 11:
                tempArr.append(0) # no go out of bounce
            elif board[x][y] == 3 and state['can_kick']==True:
                tempArr.append(1) # can kick bomb
            else:
                tempArr.append(0) # free to go here
        layer.append(tempArr)
    layer[4][4] = 0 ## we are here !
    
    return layer

def createLayerPowerUp(state):
    posX = state["position"][0]
    posY = state["position"][1]
    board = state["board"]
    layer = []
    for x in range(posX - 4, posX + 5):
        tempArr = []
        for y in range(posY - 4, posY + 5):
            if x < 0 or y < 0 or x >= 11 or y >= 11:
                tempArr.append(0) # no go out of bounce
            elif board[x][y] == 6 or board[x][y] == 7 or board[x][y] == 8:
                tempArr.append(1) # powerup here
            else:
                tempArr.append(0) # free to go here
        layer.append(tempArr)
    layer[4][4] = 0 ## we are here !
    
    return layer
    #'blast_strength': 2, 'can_kick': False, 'teammate': <Item.AgentDummy: 9>, 'ammo': 1,

    
def canSetBombMap(state):
    posX = state["position"][0]
    posY = state["position"][1]
    board = state["board"]
    layer = []
    for x in range(posX - 4, posX + 5):
        tempArr = []
        for y in range(posY - 4, posY + 5):
            if x < 0 or y < 0 or x >= 11 or y >= 11:
                tempArr.append(0) # no go out of bounce
            elif board[x][y] == 1 or board[x][y] == 2 or board[x][y] == 3 or board[x][y] == 11 or board[x][y] == 12 or board[x][y] == 13:
                tempArr.append(0) # wall or other obstical
            else:
                if int(state['ammo'])>0:
                    tempArr.append(1)
                else:
                    tempArr.append(0)
                
        layer.append(tempArr)    
    return layer
    
def createLayerWalkable(state):
    posX = state["position"][0]
    posY = state["position"][1]
    board = state["board"]
    layer = []
    for x in range(posX - 4, posX + 5):
        tempArr = []
        for y in range(posY - 4, posY + 5):
            if x < 0 or y < 0 or x >= 11 or y >= 11:
                tempArr.append(0) # no go out of bounce
            elif board[x][y] == 1 or board[x][y] == 2 or board[x][y] == 3 or board[x][y] == 11 or board[x][y] == 12 or board[x][y] == 13:
                tempArr.append(0) # wall or other obstical
            else:
                tempArr.append(1) # free to go here
        layer.append(tempArr)
    layer[4][4] = 1 ## we are here !
    
    return layer

def makeLayerDrawable(layer):
    draw = []
    Min = 0
    Max = 1
    for x in layer:
        for y in x:
            Min = min(Min, y)
            Max = max(Max, y)
    for x in layer:
        l = []
        for y in x:
            v = int((y - Min) / (Max - Min) * 255)
            l.append([v, v, v])
        draw.append(l)
    return draw

def stateToTorch(state):
    agentInfo = [
            createLayerWalkable(state[0]),
            createLayerBoxes(state[0]),
            createLayerDangerMap(state[0]),
            createLayerFriendsAndEnemies(state[0]),
            createLayerPowerUp(state[0]),
            canSetBombMap(state[0]),
            canKickMap(state[0])
        ]
    agentInfo = np.array(agentInfo)
    agentInfo = np.reshape(agentInfo, 7*9*9)
    agentInfo = torch.from_numpy(agentInfo).type(torch.FloatTensor)
    agentInfo = agentInfo.view(7, 9, 9)
    agentInfo = Variable(agentInfo)
    agentInfo = agentInfo.unsqueeze(0)
    return agentInfo