from typing import Union


from quadratic_rational import QuadraticRational, sqrt


class Point:
	def __init__(self, x: QuadraticRational, y: QuadraticRational, z: QuadraticRational):
		assert (x ** 2 + y ** 2) * sqrt(2) == z ** 2 - 1, f"{x ** 2 + y ** 2}, {z ** 2 - 1}"

		self.x = x
		self.y = y
		self.z = z

	def __repr__(self) -> str:
		return f"Point(x={self.x}, y={self.y}, z={self.z})"


def cosh_distance(point_1: Point, point_2: Point) -> QuadraticRational:
	return point_1.z * point_2.z - (point_1.x * point_2.x + point_1.y * point_2.y) * sqrt(2)		



def main():
	point_1 = Point(0, sqrt(2) / sqrt(3), (sqrt(2) + 1) / sqrt(3))
	point_2 = Point(sqrt(2) / 2, - 1 / sqrt(6), (sqrt(2) + 1) / sqrt(3))
	point_3 = Point(- sqrt(2) / 2, - 1 / sqrt(6), (sqrt(2) + 1) / sqrt(3))

	print(point_1)
	print(point_2)
	print(point_3)

	print(cosh_distance(point_1, point_2))
	print(cosh_distance(point_1, point_3))
	print(cosh_distance(point_2, point_3))


main()
