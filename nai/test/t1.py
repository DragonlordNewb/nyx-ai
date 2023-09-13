from nai.core import NyxAI
from nai.engine import *

from random import randint

def update(self, location: Entity, movement: Entity) -> Entity:
	nx = location.value("x") + movement.value("x")
	ny = location.value("y") + movement.value("y")
	nz = location.value("z") + movement.value("z")
	return Entity(
		ScalarProperty("x", nx),
		ScalarProperty("y", ny),
		ScalarProperty("z", nz)
	)

moveX = NyxAI.Action(Entity(
	ScalarProperty("x", 1),
	ScalarProperty("y", 0),
	ScalarProperty("z", 0)
))

moveY = NyxAI.Action(Entity(
	ScalarProperty("x", 0),
	ScalarProperty("y", 1),
	ScalarProperty("z", 0)
))

moveZ = NyxAI.Action(Entity(
	ScalarProperty("x", 0),
	ScalarProperty("y", 0),
	ScalarProperty("z", 1)
))

targetLocation = Entity(
	ScalarProperty("x", 100),
	ScalarProperty("y", 200),
	ScalarProperty("z", 300)
)

def passive(self):
	return self.actions[randint(0,2)]

ai = NyxAI(
	state=Entity(
		ScalarProperty("x", 0),
		ScalarProperty("y", 0),
		ScalarProperty("z", 0)
	),
	interface=update,
	actions=[moveX, moveY, moveZ],
	passiveLearning=passive
)

# Training cycle
ai.direct(targetState)
ai.execute(10000)

# activate
print(ai.currentScore())
ai.activate()
ai.execute(10000)
print(ai.currentScore()) # ideally should be higher