import argparse
import re
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene, QGraphicsView, QGraphicsRectItem
from PyQt5.QtGui import QColor
# Removed unused import of Qt
from colorama import Fore, init

init(autoreset=True)

class PImgParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.config = {}
        self.image = []
        self._validate_and_parse()

    def _validate_and_parse(self):
        try:
            with open(self.filepath, 'r') as file:
                content = file.read()
        except FileNotFoundError:
            raise ValueError(f"File not found: {self.filepath}")

        if '--CONFIG-START--' not in content or '--CONFIG-END--' not in content or \
           '--IMAGE-START--' not in content or '--IMAGE-END--' not in content:
            raise ValueError("This is not a valid ProgImage file")

        config_section = re.search(r'--CONFIG-START--(.*?)--CONFIG-END--', content, re.DOTALL)
        image_section = re.search(r'--IMAGE-START--(.*?)--IMAGE-END--', content, re.DOTALL)

        if not config_section or not image_section:
            raise ValueError("Invalid ProgImage file structure")

        self._parse_config(config_section.group(1))
        self._parse_image(image_section.group(1))

    def _parse_config(self, config_text):
        for line in config_text.strip().splitlines():
            key, value = line.split('=')
            try:
                self.config[key.strip()] = int(value.strip()) if value.strip().isdigit() else value.strip()
            except ValueError:
                raise ValueError(f"Invalid config value: {value.strip()}")

    def _parse_image(self, image_text):
        for line in image_text.strip().splitlines():
            match = re.match(r'\d+=\[(.+)\]', line)
            if match:
                row = []
                for part in match.group(1).split('+'):
                    part = part.strip()
                    rgb_match = re.match(r'rgb\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\)', part)
                    if rgb_match:
                        color = tuple(int(x) for x in rgb_match.groups())
                        row.append(color)
                    else:
                        repeat_match = re.match(r'\[rgb\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\)(?:\]\*(\d+))?', part)
                        if repeat_match:
                            try:
                                groups = repeat_match.groups()
                                r, g, b = map(int, groups[:3])
                                repeat = int(groups[3]) if groups[3] else 1
                                color = (r, g, b)
                                row.extend([color] * repeat)
                            except (ValueError, TypeError):
                                raise ValueError(f"Invalid color or repeat value in image part: {part}")
                        else:
                            raise ValueError(f"Invalid image part format: {part}")
                self.image.append(row)

    def get_config(self):
        return self.config

    def get_image(self):
        return self.image


class CLIViewer:
    def __init__(self, image):
        self.image = image

    def display(self):
        for row in self.image:
            print(''.join(self._color_to_fore(color) for color in row))

    def _color_to_fore(self, color):
        if isinstance(color, str):
            color_map = {
                "BLACK": Fore.BLACK,
                "RED": Fore.RED,
                "GREEN": Fore.GREEN,
                "YELLOW": Fore.YELLOW,
                "BLUE": Fore.BLUE,
                "MAGENTA": Fore.MAGENTA,
                "CYAN": Fore.CYAN,
                "WHITE": Fore.WHITE,
            }
            return color_map.get(color.upper(), Fore.RESET) + '█'
        elif isinstance(color, tuple):
            return Fore.RESET + '█'
        return Fore.RESET + ' '


class GUIViewer(QMainWindow):
    def __init__(self, config, image):
        super().__init__()
        self.config = config
        self.image = image
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("ProgImage Viewer")
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.setCentralWidget(self.view)
        self.resize(600, 600)

        sizex, sizey = self.config['sizex'], self.config['sizey']
        if sizex == 0 or sizey == 0:
            raise ValueError("Config 'sizex' or 'sizey' cannot be zero")
        pixsize_x = (self.width() / sizex) - 1
        pixsize_y = (self.height() / sizey) - 1

        for y, row in enumerate(self.image):
            for x, color in enumerate(row):
                rect = QGraphicsRectItem(x * pixsize_x, y * pixsize_y, pixsize_x, pixsize_y)
                if isinstance(color, tuple):
                    rect.setBrush(QColor(*color))
                self.scene.addItem(rect)


def main():
    parser = argparse.ArgumentParser(description="ProgImage Viewer")
    parser.add_argument("file", help="Path to the .pimg file")
    parser.add_argument("-c", "--console", action="store_true", help="Display image in console")
    parser.add_argument("-f", "--force", action="store_true", help="Force accept other file formats")
    args = parser.parse_args()

    try:
        pimg = PImgParser(args.file)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    config = pimg.get_config()
    image = pimg.get_image()

    if args.console or config.get('t') == 'c':
        viewer = CLIViewer(image)
        viewer.display()
    elif config.get('t') == 'g':
        app = QApplication(sys.argv)
        viewer = GUIViewer(config, image)
        viewer.show()
        sys.exit(app.exec_())
    else:
        print("Error: Unknown display type in config")
        sys.exit(1)


if __name__ == "__main__":
    main()