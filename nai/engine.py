from typing import Union
from typing import Iterable
from typing import Any
from typing import Callable

from functools import cache

Scalar = Union[int, float, complex]

# ===== BASIC DEFINITIONS ===== #

class Comparable:
	def __mod__(self, other) -> Scalar:
		return self.similarity(other)
	
	def __matmul__(self, other) -> Scalar:
		return self.difference(other)
	
	def similarity(self, other) -> Scalar:
		return 0.5 ** abs(self @ other)
	
	def difference(self, other) -> Scalar:
		return 0.5 ** abs(self % other)
	
class Property(Comparable):
	def __init__(self, name: str, value: Any) -> None:
		self.name = name
		self.value = value

	def __repr__(self) -> int:
		return "<" + type(self).__name__ + " " + repr(self.name) + "=" + repr(self.value) + ">"
	
# ===== PROPERTY TYPES ===== #

class ScalarProperty(Property):
	def similarity(self, other: "ScalarProperty") -> Scalar:
		return 0.5 ** abs(abs(self.value) - abs(other.value))
	
class HammingProperty(Property):
	def difference(self, other: "HammingProperty") -> Scalar:
		return sum([1 for x, y in zip(self, other) if x != y])
	
class LevenshteinProperty(Property):
	@staticmethod
	def lev(a, b):
		if len(a) == 0:
			return len(b)
		if len(b) == 0:
			return len(a)
		
		try:
			if a[0] == b[0]:
				return LevenshteinProperty.lev(a[1:], b[1:])
		except:
			pass
		finally:
			return 1 + min(
				LevenshteinProperty.lev(a, b[1:]),
				LevenshteinProperty.lev(a[1:], b),
				LevenshteinProperty.lev(a[1:], b[1:])
			)
		
	def difference(self, other: "LevenshteinProperty") -> Scalar:
		return self.lev(self.value, other.value) / max([len(self.value), len(other.value)])

class EqualityProperty(Property):
	def similarity(self, other: "EqualityProperty") -> int:
		if self.value == other.value:
			return 1
		return 0
	
	def difference(self, other: "EqualityProperty") -> int:
		if self.value != other.value:
			return 1
		return 0
	
# ===== ENTITY DEFINITION ===== #

class Entity(Comparable):
	def __init__(self, *properties: tuple[Property]) -> None:
		self.properties = properties
		if len(self.signature()) != len(self.properties):
			raise NameError("Probable property duplicate name.")

	@cache
	def signature(self) -> list[str]:
		return sorted(list(set([property.name for property in self])))

	def property(self, name: str) -> Property:
		for property in self:
			if property.name == name:
				return property
		raise KeyError("Entity doesn\'t have a property named " + repr(name) + ".")

	def value(self, name: str) -> Any:
		return self.property(name).value
	
	# Comparison operators

	def __gt__(self, other: "Entity") -> bool:
		return self.super(other)

	def super(self, other: "Entity") -> bool:
		sig = other.signature()
		for item in self.signature():
			if item not in sig:
				return False
		return True
	
	def __lt__(self, other: "Entity") -> bool:
		return self.sub(other)

	def sub(self, other: "Entity") -> bool:
		sig = self.signature()
		for item in other.signature():
			if item not in sig:
				return False
		return True

	def __ge__(self, other: "Entity") -> bool:
		return self > other or self == other
	
	def __le__(self, other: "Entity") -> bool:
		return self < other or self == other

	def __eq__(self, other: "Entity") -> bool:
		return self.equal(other)
	
	def equal(self, other: "Entity") -> bool:
		return self.signature() == other.signature()
	
	def __sub__(self, other: "Entity") -> list[str]:
		return self.kernel(other)

	def kernel(self, *others: tuple["Entity"]) -> list[str]:
		sigs = [set(entity.signature()) for entity in others]
		sig = set(self.signature())
		for s in sigs:
			sig &= s
		return sorted(list(sig))

	def __add__(self, other: "Entity") -> list[str]:
		return self.union(other)
	
	def union(self, *others: tuple["Entity"]) -> list[str]:
		sigs = [set(entity.signature()) for entity in others]
		sig = set(self.signature())
		for s in sigs:
			sig |= s
		return sorted(list(sig))
	
	# Similarity operators

	def similarity(self, other: "Entity") -> Scalar:
		if self < other:
			return other.similarity(self)
		
		s = 1

		for item in self.signature():
			s *= self.property(item) % other.property(item)

		return s
	
	def difference(self, other: "Entity") -> Scalar:
		if self < other: 
			return other.difference(self)
		
		d = 1

		for item in self.signature():
			d *= self.property(item) @ other.property(item)

		return d