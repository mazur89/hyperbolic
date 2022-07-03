from quadratic_rational import sqrt
from tiling import Vertex, Tiling


def main():
    point_1 = Vertex(0 * sqrt(2) / 1, sqrt(2) / sqrt(3), (sqrt(2) + 1) / sqrt(3))
    point_2 = Vertex(- sqrt(2) / 2, - 1 / sqrt(6), (sqrt(2) + 1) / sqrt(3))
    point_3 = Vertex(sqrt(2) / 2, - 1 / sqrt(6), (sqrt(2) + 1) / sqrt(3))

    tiling = Tiling(point_1, point_2, point_3)
    tiling.create_tiles(depth=6)


if __name__ == "__main__":
    main()
