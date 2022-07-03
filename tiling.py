from typing import Set
from drawSvg import Drawing
import os
import yaml


from quadratic_rational import QuadraticRational, sqrt


class Point:
	__slots__ = ("x", "y", "z")

	def __init__(self, x: QuadraticRational, y: QuadraticRational, z: QuadraticRational):

		self.x = QuadraticRational.convert(x)
		self.y = QuadraticRational.convert(y)
		self.z = QuadraticRational.convert(z)

	@property
	def poincare(self) -> complex:
		return (self.x.value + self.y.value * 1j) * 2 ** 0.25 / (1 + self.z.value)	
	
	@property
	def x_euclid(self) -> float:
		return self.poincare.real

	@property
	def y_euclid(self) -> float:
		return self.poincare.imag

	def __eq__(self, other: "Point") -> bool:
		return self.x == other.x and self.y == other.y

	def __hash__(self) -> int:
		return hash(
			(
				self.x, 
				self.y,
			)
		)	

	def __repr__(self) -> str:
		return f"Point(x={self.x_euclid.value * 2 ** 0.25}, y={self.y_euclid.value * 2 ** 0.25})"

	def to_json(self):
		return {"x": self.x.to_json(), "y": self.y.to_json(), "z": self.z.to_json()}

	@classmethod
	def from_json(cls, data):
		return cls(
			x=QuadraticRational.from_json(data["x"]),
			y=QuadraticRational.from_json(data["y"]),
			z=QuadraticRational.from_json(data["z"]),
		)


class Line:
	__slots__ = ("x", "y", "z")

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

	def reflection(self, point: Point) -> Point:
		factor = self.product(point) / self.norm

		x = point.x + 2 * self.x * factor
		y = point.y + 2 * self.y * factor
		z = point.z + 2 * self.z * factor

		return type(point)(x, y, z)

	@property
	def r_euclid(self) -> float:
		assert self.z != 0

		return (((self.x / self.z) ** 2 + (self.y / self.z) ** 2) * sqrt(2) - 1).value ** 0.5

	@property
	def poincare(self) -> complex:
		assert self.z != 0

		return (self.x.value + self.y.value * 1j) * 2 ** 0.25 / self.z.value

	@property
	def x_euclid(self) -> float:
		return self.poincare.real

	@property
	def y_euclid(self) -> float:
		return self.poincare.imag

	def to_json(self):
		return {"x": self.x.to_json(), "y": self.y.to_json(), "z": self.z.to_json()}

	@classmethod
	def from_json(cls, data):
		return cls(
			x=QuadraticRational.from_json(data["x"]),
			y=QuadraticRational.from_json(data["y"]),
			z=QuadraticRational.from_json(data["z"]),
		)


def cosh_distance(point_1: Point, point_2: Point) -> QuadraticRational:
	return point_1.z * point_2.z - (point_1.x * point_2.x + point_1.y * point_2.y) * sqrt(2)		


class Vertex(Point):
	pass


class Edge:
	__slots__ = ("vertex_1", "vertex_2")

	def __init__(self, vertex_1: Vertex, vertex_2: Vertex):
		
		self.vertex_1 = vertex_1
		self.vertex_2 = vertex_2
	
	@property
	def vertices(self) -> Set[Vertex]:
		return {self.vertex_1, self.vertex_2}

	def __eq__(self, other):
		return self.vertices == other.vertices

	def __hash__(self) -> int:
		return hash(self.vertex_1) + hash(self.vertex_2)

	def to_json(self):
		return [self.vertex_1, self.vertex_2]

	@classmethod
	def from_json(cls, data: list):
		return cls(Vertex.from_json(data[0]), Vertex.from_json(data[1]))


class Tile:
	__slots__ = ("vertex_1", "vertex_2", "vertex_3")

	def __init__(self, vertex_1: Vertex, vertex_2: Vertex, vertex_3: Vertex):
		self.vertex_1 = vertex_1
		self.vertex_2 = vertex_2
		self.vertex_3 = vertex_3

	def toDrawables(self, elements, **kwargs):
		path = elements.Path(**kwargs)
		self.drawToPath(path)
		path.Z()
		return (path,)

	def drawToPath(self, path):
		path.M(self.vertex_1.x_euclid, self.vertex_1.y_euclid)
		for start, end in [(self.vertex_1, self.vertex_2), (self.vertex_2, self.vertex_3), (self.vertex_3, self.vertex_1)]:
			r = Line.from_points(start, end).r_euclid
			cw = start.x_euclid * end.y_euclid > start.y_euclid * end.x_euclid
			path.A(r, r, 0, 0, cw, end.x_euclid, end.y_euclid)
	
	@property
	def vertices(self) -> Set[Vertex]:
		return {self.vertex_1, self.vertex_2, self.vertex_3}

	def __eq__(self, other):
		return self.vertices == other.vertices	

	def __hash__(self):
		return hash(self.vertex_1) + hash(self.vertex_2) + hash(self.vertex_3)

	def to_json(self):
		return [self.vertex_1.to_json(), self.vertex_2.to_json(), self.vertex_3.to_json()]

	@classmethod
	def from_json(cls, data):
		return cls(Vertex.from_json(data[0]), Vertex.from_json(data[1]), Vertex.from_json(data[2]))


class Tiling:
	def __init__(self, vertex_1: Vertex, vertex_2: Vertex, vertex_3: Vertex):
		self._vertices = {}
		self._edges = {}
		self._tiles = {}

		self._edges_to_tiles = {}

		self._tiles_to_colours = {}
		self._vertices_to_colours = {}
	
		self._boundary = [vertex_1, vertex_2, vertex_3]

		self._colour_values = ["#ffffff", "#000000", "#cc6600", "#66cc00"]

		self._populate_data()

	def _populate_data(self):
		for index, vertex in enumerate(self._boundary):
			self._vertices[vertex] = vertex
			
			edge = Edge(*tuple(set(self._boundary) - {vertex}))
			self._edges[edge] = edge

			self._vertices_to_colours[vertex] = index + 1

		tile = Tile(*self._boundary)
		self._tiles[tile] = tile

		self._tiles_to_colours[tile] = 0

		for edge in self._edges:
			self._edges_to_tiles[edge] = {tile}

	def _build_new_tile(self, vertex_1: Vertex, vertex_2: Vertex) -> Vertex:
		edge = self._edges[Edge(vertex_1, vertex_2)]
		
		inner_tile = tuple(self._edges_to_tiles[edge])[0]
		inner_vertex = tuple(inner_tile.vertices - {vertex_1, vertex_2})[0]

		reflected_vertex = Line.from_points(vertex_1, vertex_2).reflection(inner_vertex)

		reflected_vertex = self._add_vertex(reflected_vertex)

		self._add_edge(Edge(vertex_1, reflected_vertex))
		self._add_edge(Edge(vertex_2, reflected_vertex))

		new_tile = self._add_tile(Tile(vertex_1, reflected_vertex, vertex_2))
		
		self._vertices_to_colours[reflected_vertex] = self._vertices_to_colours[inner_vertex]
		self._tiles_to_colours[new_tile] = self._vertices_to_colours[inner_vertex] ^ self._tiles_to_colours[inner_tile]

		return reflected_vertex

	def _add_vertex(self, vertex: Vertex) -> Vertex:
		if vertex not in self._vertices:
			self._vertices[vertex] = vertex

		return self._vertices[vertex]

	def _add_edge(self, edge: Edge):
		if edge not in self._edges:
			self._edges[edge] = edge
			self._edges_to_tiles[edge] = set()
		
	def _add_tile(self, tile: Tile):
		if tile not in self._tiles:
			self._tiles[tile] = tile

		tile = self._tiles[tile]
		
		edge_1 = self._edges[Edge(tile.vertex_2, tile.vertex_3)]
		edge_2 = self._edges[Edge(tile.vertex_3, tile.vertex_1)]
		edge_3 = self._edges[Edge(tile.vertex_1, tile.vertex_2)]
		
		self._edges_to_tiles[edge_1].add(tile)
		self._edges_to_tiles[edge_2].add(tile)
		self._edges_to_tiles[edge_3].add(tile)

		return tile
	
	def _save_data(self, depth: int, path: str):
		with open(os.path.join(path, 'logo-depth-{}-data.yaml'.format(depth)), 'w') as f:
			yaml.safe_dump([(key.to_json(), int(value)) for key, value in self._tiles_to_colours.items()], f, indent=2)

	def create_tiles(self, depth: int):
		if depth == 0:
			self._save_data(depth, path="images")
			return

		self.create_tiles(depth=depth-1)
		
		print(f"Populating depth {depth}...")
		new_boundary = [self._build_new_tile(self._boundary[0], self._boundary[-1])]
		index = 0

		counter = 0
		num_tiles = (3 * sqrt(3) * ((2 + sqrt(3)) ** depth - (2 - sqrt(3)) ** depth)).as_int()

		while True:
			new_vertex = self._build_new_tile(new_boundary[-1], self._boundary[index])
			counter += 1
			print(f"created {counter} / {num_tiles} tiles...", end="\r")

			if new_vertex in self._boundary:
				index += 1
			elif new_vertex in new_boundary:
				break
			else:
				new_boundary.append(new_vertex)

		self._boundary = new_boundary
		self._save_data(depth, path="images")

		print(f"Populated, found {len(self._tiles)} tiles")
