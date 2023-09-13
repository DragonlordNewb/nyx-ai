from nai.engine import *

class NyxAI:

	# ===== Components ===== #

	class Action:
		def __init__(self, desc: Entity) -> None:
			self.desc = desc
			self.history: list[tuple[Entity, Entity, Entity]] = []

		def __iter__(self) -> Iterable[tuple[Entity, Entity, Entity]]:
			return iter(self.history)

		def record(self, targetState: Entity, initialState: Entity, finalState: Entity) -> None:
			self.history.append((targetState, initialState, finalState))

		def score(self, targetState: Entity, initialState: Entity) -> Scalar:
			s: Scalar = 0

			for target, initial, final in self:
				targetSimilarity = target % targetState
				initialSimilarity = initial % initialState
				applicability = targetSimilarity * initialSimilarity

				initialScore = initial % target
				finalScore = final % target
				delta = finalScore - initialScore

				s += delta * applicability

			return s

	state: Entity = None
	interface: Callable[[Entity, Entity], Entity] = None
	actions: list[Action] = []
	_ready: bool = False

	@property
	def ready(self) -> bool:
		return self._ready
	
	@ready.getter
	def ready(self) -> bool:
		r = self.state != None and self.interface != None and len(self.actions) > 0
		self._ready = r
		return self._ready
	
	@ready.setter
	def ready(self) -> bool:
		raise SyntaxError("Readiness can\'t be directly set.")
	
	# ===== Main methods ===== #

	def __init__(self, state: Entity=None, interface: Callable[[Entity, Entity], Entity]=None, actions: list[Action]=[])