
from dataclasses import dataclass

from pyautogui import Point


@dataclass
class Vector2:
    x: float
    y: float

    def __add__(self, other):
        if not isinstance(other, Vector2):
            return NotImplemented
        return Vector2(self.x + other.x, self.y + other.y)



@dataclass
class Direction:
    xAxis: float
    yAxis: float

class HitBox:
    def __init__(self, position: Vector2, width: float, height: float):
        self.position = position
        self.width = width
        self.height = height
        self.topRight = Vector2((width/2), (height/2))
        self.bottomLeft = Vector2(-(width/2), -(height/2))


    
    def GetCurrentTopRight(self):
        return self.topRight + self.position
    
    def GetCurrentBottomLeft(self):
        return self.bottomLeft + self.position


    def checkCollision(self, otherHitBox: HitBox):
        hitBoxMax = self.GetCurrentTopRight()
        hitBoxMin = self.GetCurrentBottomLeft()
        

        otherHitBox_Max = otherHitBox.GetCurrentTopRight()
        otherHitBoxMin = otherHitBox.GetCurrentBottomLeft()

        overlapX = hitBoxMin.x <= otherHitBox_Max.x and hitBoxMax.x >= otherHitBoxMin.x
        overlapY = hitBoxMin.y <= otherHitBox_Max.y and hitBoxMax.y >= otherHitBoxMin.y

        return overlapX and overlapY


