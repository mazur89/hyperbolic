import os
import tqdm

import yaml
from drawSvg import Drawing

from tiling import Tile

colour_values = ["#ffffff", "#000000", "#cc6600", "#66cc00"]


def _draw_from_data(depth: int, path: str):
    print(f"Loading data for depth {depth}...")

    with open(os.path.join(path, 'logo-depth-{}-data.yaml'.format(depth)), 'r') as f:
        data = yaml.safe_load(f)
        data = {Tile.from_json(key): value for key, value in data}

    print("Loaded. Drawing...")

    drawing = Drawing(2, 2, origin='center')
    drawing.setRenderSize(4096)

    for tile, colour_index in tqdm.tqdm(data.items()):
        drawing.draw(tile, fill=colour_values[colour_index])

    drawing.saveSvg(os.path.join(path, 'logo-depth-{}.svg'.format(depth)))

    print("Drawn.")


def main():
    for depth in range(7):
        _draw_from_data(depth, path="images")


if __name__ == "__main__":
    main()
