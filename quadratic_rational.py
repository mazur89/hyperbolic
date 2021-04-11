import numpy as np
from typing import Tuple, Union


class QuadraticIntegerMeta(type):
	__cache__ = {}

	def __new__(mcs, name, bases, attributes, **kwargs):
		if attributes["__numbers__"] not in mcs.__cache__:
			mcs.__cache__[attributes["__numbers__"]] = super().__new__(mcs, name, bases, attributes, **kwargs)

		return mcs.__cache__[attributes["__numbers__"]]

	def __getitem__(cls, numbers: Union[int, Tuple[int, ...]]):
		if not isinstance(numbers, tuple):
			numbers = (numbers,)

		products = cls._get_products_from_numbers(numbers)
		products = cls._get_products_from_numbers(tuple(products.flatten()))
		numbers = cls._get_numbers_from_products(products)
		
		return type(cls)(
			f"{cls.__name__}[{', '.join([str(number) for number in numbers])}]",
			(cls,),
			{"__numbers__": numbers, "__products__": products},
		)
		
	def _get_products_from_numbers(cls, numbers: Tuple[int, ...]) -> np.ndarray:
		products = np.array(1)

		for number in sorted(numbers):
			if number in products:
				continue

			gcd = np.gcd(products, number)
			products = products[None] * np.array([1, number]).reshape((2,) + (1,) * products.ndim)
			products[1] //= gcd ** 2

		return products

	def _get_numbers_from_products(cls, products: np.ndarray) -> Tuple[int, ...]:
		numbers = []
		
		for axis in range(products.ndim):
			index = [0] * products.ndim
			index[axis] = 1
			numbers.append(products[tuple(index)])
		
		return reversed(tuple(numbers))


class QuadraticInteger(metaclass=QuadraticIntegerMeta):
	__numbers__ = ()
	__products__ = np.array(1)

	def __init__(self, coefficients: np.ndarray):
		assert coefficients.shape == self.__products__.shape
		self.coefficients = coefficients
	
	def as_int(self) -> int:
		assert self.__products__.ndim == 0, "{self} cannot be represented as an integer"
		return int(self.coefficients)

	@staticmethod
	def convert(number: Union[int, "QuadraticInteger"]) -> "QuadraticInteger":
		if not isinstance(number, QuadraticInteger):
			return QuadraticInteger(np.array(number))
		return number

	def rebase(self, numbers: Tuple[int, ...]) -> "QuadraticInteger":
		new_quadratic_integer = QuadraticInteger[numbers]

		self_products = self.__products__
		new_products = new_quadratic_integer.__products__

		products_mapping = new_products.reshape(new_products.shape + (1,) * self_products.ndim) == self_products
		assert np.all(products_mapping.sum(axis=tuple(range(new_products.ndim))) >= (self.coefficients != 0))
		
		new_coefficients = np.sum(self.coefficients * products_mapping, axis=tuple(range(-self_products.ndim, 0)))
		return new_quadratic_integer(new_coefficients)

	def reduce(self) -> "QuadraticInteger":
		numbers = self.__products__[self.coefficients != 0]
		return self.rebase(tuple(numbers.flatten()))
	
	def __neg__(self) -> "QuadraticInteger":
		return type(self)(-self.coefficients)
	
	def __add__(self, other: Union[int, "QuadraticInteger"]) -> "QuadraticInteger":
		other = QuadraticInteger.convert(other)

		new_numbers = tuple(self.__products__.flatten()) + tuple(other.__products__.flatten())
		
		summand_1 = self.rebase(new_numbers)
		summand_2 = other.rebase(new_numbers)
		
		return type(summand_1)(summand_1.coefficients + summand_2.coefficients).reduce()

	def __radd__(self, other: Union[int, "QuadraticInteger"]) -> "QuadraticInteger":
		return self + other

	def __sub__(self, other: Union[int, "QuadraticInteger"]) -> "QuadraticInteger":
		return self + (-other)

	def __rsub__(self, other: Union[int, "QuadraticInteger"]) -> "QuadraticInteger":
		return -self + other

	def __mul__(self, other: Union[int, "QuadraticInteger"]) -> "QuadraticInteger":
		other = QuadraticInteger.convert(other)

		new_numbers = tuple(self.__products__.flatten()) + tuple(other.__products__.flatten())
		
		factor_1 = self.rebase(new_numbers)
		factor_2 = other.rebase(new_numbers)

		products = factor_1.__products__
		products_reshaped = factor_2.__products__.reshape(factor_2.__products__.shape + (1,) * factor_1.__products__.ndim)
		
		products_gcd = np.gcd(products, products_reshaped)
		products_overall = products * products_reshaped // products_gcd ** 2
		result = (products.reshape(products.shape + (1,) * products_gcd.ndim) == products_overall) * products_gcd
		
		result = np.sum(result * factor_1.coefficients, axis=tuple(range(-products.ndim, 0)))
		result = np.sum(result * factor_2.coefficients, axis=tuple(range(-products.ndim, 0)))
		
		return type(factor_1)(result).reduce()

	def __rmul__(self, other: Union[int, "QuadraticInteger"]) -> "QuadraticInteger":
		return self * other

	def __truediv__(self, other: Union[int, "QuadraticInteger"]) -> "QuadraticRational":
		return QuadraticRational(self, other)

	def __rtruediv__(self, other: Union[int, "QuadraticInteger"]) -> "QuadraticRational":
		return QuadraticRational(other, self)
	
	def __eq__(self, other: Union[int, "QuadraticInteger"]) -> bool:
		other = QuadraticInteger.convert(other)
		return np.all(self.__products__ == other.__products__) and np.all(self.coefficients == other.coefficients)

	def __repr__(self) -> str:
		res = ""
		
		for coefficient, product in zip(self.coefficients.flatten(), self.__products__.flatten()):
			if coefficient == 0:
				continue
			
			if coefficient < 0:
				res += " -"
			elif res != "":
				res += " +"

			if abs(coefficient) > 1 or product == 1:
				res += f" {abs(coefficient)}"

			if product > 1:
				if abs(coefficient) > 1:
					res += " *"
				res += f" sqrt({product})"

			if res.startswith(" "):
				res = res[1:]
		
		if res == "":
			return "0"
		return res


class QuadraticRational:
	def __init__(self, numerator: Union[int, QuadraticInteger], denominator: Union[int, QuadraticInteger]):
		if isinstance(denominator, QuadraticInteger):
			while denominator.__products__.ndim > 0:
				factor = type(denominator)(denominator.coefficients * np.array([1, -1]))
				
				numerator = numerator * factor
				denominator = denominator * factor
		
			denominator = denominator.as_int()

		if denominator < 0:
			numerator = -numerator
			denominator = -denominator

		numerator = QuadraticInteger.convert(numerator)

		self.numerator = numerator
		self.denominator = denominator

		self._reduce_fraction()

	def _reduce_fraction(self):
		numerator_gcd = self.numerator.coefficients
		while numerator_gcd.ndim > 0:
			numerator_gcd = np.gcd(numerator_gcd[0], numerator_gcd[1])
		
		factor = int(np.gcd(numerator_gcd, self.denominator))

		self.numerator.coefficients //= factor
		self.denominator //= factor
	
	@staticmethod
	def convert(number: Union[int, QuadraticInteger, "QuadraticRational"]):
		if not isinstance(number, QuadraticRational):
			return QuadraticRational(number, 1)
		return number
	
	def __neg__(self) -> "QuadraticRational":
		return type(self)(-self.numerator, self.denominator)

	def __add__(self, other: Union[int, QuadraticInteger, "QuadraticRational"]) -> "QuadraticRational":
		other = QuadraticRational.convert(other)

		numerator = self.numerator * other.denominator + other.numerator * self.denominator
		denominator = self.denominator * other.denominator

		return QuadraticRational(numerator, denominator)

	def __radd__(self, other: Union[int, QuadraticInteger, "QuadraticRational"]) -> "QuadraticRational":
		return self + other
		
	def __sub__(self, other: Union[int, QuadraticInteger, "QuadraticRational"]) -> "QuadraticRational":
		return self + (-other)
		
	def __rsub__(self, other: Union[int, QuadraticInteger, "QuadraticRational"]) -> "QuadraticRational":
		return -self + other

	def __mul__(self, other: Union[int, QuadraticInteger, "QuadraticRational"]) -> "QuadraticRational":
		other = QuadraticRational.convert(other)

		numerator = self.numerator * other.numerator
		denominator = self.denominator * other.denominator

		return QuadraticRational(numerator, denominator)

	def __rmul__(self, other: Union[int, QuadraticInteger, "QuadraticRational"]) -> "QuadraticRational":
		return self * other

	def __truediv__(self, other: Union[int, QuadraticInteger, "QuadraticRational"]) -> "QuadraticRational":
		if isinstance(other, int):
			other = QuadraticInteger.from_int(other)
		if isinstance(other, QuadraticInteger):
			other = QuadraticRational(other, 1)

		numerator = self.numerator * other.denominator
		denominator = self.denominator * other.numerator

		return QuadraticRational(numerator, denominator)

	def __rtruediv__(self, other: Union[int, QuadraticInteger, "QuadraticRational"]) -> "QuadraticRational":
		other = QuadraticRational.convert(other)

		return other / self

	def __pow__(self, exponent: int):
		if exponent == 0:
			return QuadraticRational.convert(1)

		if exponent < 0:
			return 1 / (self ** -exponent)

		half_exponent = exponent // 2
		half_power = self ** half_exponent

		if exponent % 2 == 0:
			return half_power * half_power
		return half_power * half_power * self

	def __eq__(self, other: Union[int, QuadraticInteger, "QuadraticRational"]):
		other = QuadraticRational.convert(other)
		return self.numerator == other.numerator and self.denominator == other.denominator
		
	def __repr__(self) -> str:
		if self.denominator == 1:
			return f"{self.numerator}"

		numerator_str = f"{self.numerator}"
		if np.sum(self.numerator.coefficients != 0) > 1:
			numerator_str = f"({self.numerator})"
		
		return f"{numerator_str} / {self.denominator}"


def sqrt(number: int) -> QuadraticInteger:
	coefficient = 1

	n = 2
	while n * n <= number:
		while number % (n * n) == 0:
			coefficient *= n
			number //= n * n
		n += 1

	return QuadraticInteger[number](np.array([0, coefficient]))

