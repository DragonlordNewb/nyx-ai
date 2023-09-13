from nai.engine import *

class NyxAI:

	class SystemFailure(RuntimeError):
		pass

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
	passiveLearning: Callable[], Action] = None
	actions: list[Action] = []
	directive: Entity = None
	_ready: bool = False
	_inControl: bool = True
	active: bool = False

	@property
	def ready(self) -> bool:
		return self._ready
	
	@ready.getter
	def ready(self) -> bool:
		r = self.state != None and self.interface != None and len(self.actions) > 0 and self.directive != None
		self._ready = r
		return self._ready
	
	@ready.setter
	def ready(self, value) -> bool:
		raise self.SystemFailure("Readiness can\'t be directly set.")

	@property
	def inControl(self) -> bool:
		return self._inControl

	@inControl.setter
	def inControl(self, value) -> None:
		if type(value) == bool:
			if value:
				print("NyxAI regained control.")
			else:
				print("NyxAI lost control.")
			self._inControl = value
		raise self.SystemFailure("inControl must be a bool.")

	@inControl.getter
	def inControl(self) -> bool:
		return self._inControl
		
	# ===== Main methods ===== #

	def __init__(self,
		     state: Entity=None,
		     interface: Callable[[Entity, Entity], Entity]=None,
		     actions: list[Action]=[],
		     directive: Entity=None,
		     passiveLearning: Callable[[], Action]=None) -> None:
		self.state, self.interface, self.actions, self.directive, self.passiveLearning = state, interface, actions, directive, passiveLearning

	def decide(self) -> Action:
		scores: tuple[Action, Scalar] = []
		highScore = 0
		
		for action in self.actions:
			score = action.score(self.directive, self.state)
			if highScore < score:
				highScore = score
			scores.append((action, score))
			
		for action, score in scores:
			if score == highScore:
				return action
				
		raise self.SystemFailure("Could not decide on an action.")
	
	def take(self, action: Action) -> None:
		if not self.ready:
			raise self.SystemFailure("NyxAI not ready to operate.")
			
		newState = self.interface(self.state, action)
					  
		if self.inControl:
			action.record(self.directive, self.state, newState)
		self.state = newState

	def activate(self) -> None:
		self.active = True

	def deactivate(self) -> None:
		self.active = False

	def execute(self, iterations: int=1) -> Entity:
		if iterations > 1:
			for _ in range(iterations - 1):
				self.execute(1)
				
		if self.active:
			action = self.decide()
			self.take(action)
		else:
			action = self.passiveLearning()
			self.take(action)
			
		return self.state
	
	def direct(self, directive: Entity) -> None:
		self.directive = directive
	
	def hijack(self, *actions: tuple[Action]) -> None:
		self.inControl = False
		for action in actions:
			self.take(action)
		self.inControl = True

	def currentScore(self) -> Scalar:
		if self.directive == None:
			return None
		return self.state % self.directive