from typing import Union


from quadratic_rational import QuadraticRational, sqrt


class Point:
	def __init__(self, x: QuadraticRational, y: QuadraticRational, z: QuadraticRational):
		assert (x ** 2 + y ** 2) * sqrt(2) == z ** 2 - 1, f"invalid coordinates: x={x}, y={y}, z={z}"

		self.x = x
		self.y = y
		self.z = z

	def __eq__(self, other: "Point") -> bool:
		return self.x == other.x and self.y == other.y

	def __repr__(self) -> str:
		return f"Point(x={self.x}, y={self.y}, z={self.z})"


class Line:
	def __init__(self, x: QuadraticRational, y: QuadraticRational, z: QuadraticRational):
		self.x = x
		self.y = y
		self.z = z

	@property
	def norm(self) -> QuadraticRational:
		return (self.x ** 2 + self.y ** 2) * sqrt(2) - self.z ** 2

	def product(self, point: Point) -> QuadraticRational:
		return self.z * point.z - (self.x * point.x + self.y * point.y) * sqrt(2)

	def __contains__(self, point: Point) -> bool:
		return self.product(point) == 0
	
	@staticmethod
	def from_points(point_1: Point, point_2: Point) -> "Line":
		return Line(
			x=point_1.y * point_2.z - point_1.z * point_2.y,
			y=point_1.z * point_2.x - point_1.x * point_2.z,
			z=(point_1.y * point_2.x - point_1.x * point_2.y) * sqrt(2),
		)

	def symmetry(self, point: Point) -> Point:
		factor = self.product(point) / self.norm

		x = point.x + 2 * self.x * factor
		y = point.y + 2 * self.y * factor
		z = point.z + 2 * self.z * factor

		return Point(x, y, z)

def cosh_distance(point_1: Point, point_2: Point) -> QuadraticRational:
	return point_1.z * point_2.z - (point_1.x * point_2.x + point_1.y * point_2.y) * sqrt(2)		



def main():
	origin = Point(0, 0, 1)
	point_1 = Point(0, sqrt(2) / sqrt(3), (sqrt(2) + 1) / sqrt(3))
	point_2 = Point(sqrt(2) / 2, - 1 / sqrt(6), (sqrt(2) + 1) / sqrt(3))
	point_3 = Point(- sqrt(2) / 2, - 1 / sqrt(6), (sqrt(2) + 1) / sqrt(3))

	assert Line.from_points(origin, point_1).symmetry(point_2) == point_3
	assert Line.from_points(origin, point_1).symmetry(point_3) == point_2
	assert Line.from_points(origin, point_2).symmetry(point_1) == point_3
	assert Line.from_points(origin, point_2).symmetry(point_3) == point_1
	assert Line.from_points(origin, point_3).symmetry(point_1) == point_2
	assert Line.from_points(origin, point_3).symmetry(point_2) == point_1


main()
