import random
import math
from Physic_Classes import Vector2, Direction, HitBox




class Ball:

    def __init__(self, position: Vector2, hitbox: HitBox, name: str, color: tuple, speed: float,
                  direction: Direction, radius: float = 10, ability: str = None,
                  Health: int = 100):

        self.position = position
        self.name = name
        self.hitbox = hitbox
        self.color = color
        self.speed = speed
        self.direction = direction
        self.Health = Health
        self.radius = radius
        self.ability = ability  

    def initialDirection(self):
        randomAngle = random.uniform(0, 2 * math.pi)
        self.direction = Direction(xAxis=math.cos(randomAngle), yAxis=math.sin(randomAngle))
    
    def move(self):
        self.position.x += self.direction.xAxis * self.speed
        self.position.y += self.direction.yAxis * self.speed


        
    