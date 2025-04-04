import sys
import argparse
import re
from PyQt5 import QtWidgets, QtGui, QtCore
from colorama import Fore, Style, init

# Инициализация colorama (для Windows)
init(autoreset=True)

# Обработка аргументов командной строки
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", help="File name to open", required=True)
args = parser.parse_args()

def parse_config(file_path):
    """
    Считывает файл конфигурации, разбивая его на глобальный блок (между --CONFIG-START-- и --CONFIG-END--)
    и блок IMAGE (между ---IMAGE-START-- и --IMAGE-END--). Для IMAGE каждая строка вида:
      <row>=[<color>[, multiplier]]+...[<color>[, multiplier]]
    Например:
      1=[BLACK, 6]
      2=[BLACK]+[WHITE, 4]+[BLACK]
    """
    global_conf = {}
    image_conf = {}
    inside_config = False
    inside_image = False

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "--CONFIG-START--":
                inside_config = True
                continue
            if line == "--CONFIG-END--":
                inside_config = False
                continue
            if line == "---IMAGE-START--":
                inside_image = True
                continue
            if line == "--IMAGE-END--":
                inside_image = False
                continue

            if inside_config and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                # Если значение состоит только из цифр, преобразуем в число
                if value.isdigit():
                    value = int(value)
                # Если в значении есть кавычки, убираем их
                elif (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                global_conf[key] = value

            if inside_image and "=" in line:
                # Формат: <row>=<segment1>+<segment2>+...
                row_str, segments_str = line.split("=", 1)
                try:
                    row = int(row_str.strip())
                except ValueError:
                    continue
                # Ищем сегменты вида +[ ... ]
                segments = re.findall(r"\+\[([^\]]+)\]", segments_str)
                parsed_segments = []
                for seg in segments:
                    parts = seg.split(",")
                    color_str = parts[0].strip()
                    multiplier = 1.0
                    if len(parts) > 1:
                        try:
                            multiplier = float(parts[1].strip())
                        except ValueError:
                            multiplier = 1.0
                    parsed_segments.append({"color": color_str, "multiplier": multiplier})
                image_conf[row] = parsed_segments

    return global_conf, image_conf

def parse_rgba(color_str):
    """
    Парсит строку вида rgba(0, 0, 0, 255) и возвращает кортеж (R, G, B, A).
    Используется для GUI режима.
    """
    m = re.match(r"rgba\(\s*(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\s*\)", color_str)
    if m:
        return tuple(map(int, m.groups()))
    return (0, 0, 0, 255)

def print_image_cli(image_conf, mode="c"):
    """
    Выводит изображение в терминале (CLI) в новом или старом стиле.
    Новый формат конфигурации: цвета задаются именами (например, BLACK, WHITE) и множитель задаётся через запятую.
    mode: "c" или "c_o"
    """
    # Словарь соответствия имён цветов ANSI (используем colorama.Fore)
    color_map = {
        "BLACK": Fore.BLACK,
        "WHITE": Fore.WHITE,
        "RED": Fore.RED,
        "GREEN": Fore.GREEN,
        "BLUE": Fore.BLUE,
        "YELLOW": Fore.YELLOW,
        "CYAN": Fore.CYAN,
        "MAGENTA": Fore.MAGENTA,
        "LIGHTBLACK": Fore.LIGHTBLACK_EX,
        "LIGHTRED": Fore.LIGHTRED_EX,
        "LIGHTGREEN": Fore.LIGHTGREEN_EX,
        "LIGHTYELLOW": Fore.LIGHTYELLOW_EX,
        "LIGHTBLUE": Fore.LIGHTBLUE_EX,
        "LIGHTCYAN": Fore.LIGHTCYAN_EX,
        "LIGHTMAGENTA": Fore.LIGHTMAGENTA_EX,
        "LIGHTWHITE": Fore.LIGHTWHITE_EX,
    }
    # Выбираем символ для отрисовки в зависимости от режима
    block_char = "█" if mode == "c" else "#"

    # Для каждого ряда, сортируя по номеру
    for row in sorted(image_conf.keys()):
        line = ""
        for seg in image_conf[row]:
            col_name = seg["color"].upper()
            ansi_color = color_map.get(col_name, Fore.RESET)
            multiplier = seg["multiplier"]
            # Для CLI увеличиваем ширину символов (умножаем количество символов на int(multiplier * 2))
            line += ansi_color + (block_char * int(multiplier * 2))
        print(line + Style.RESET_ALL)

class ImageWidget(QtWidgets.QWidget):
    def __init__(self, global_conf, image_conf):
        super().__init__()
        self.global_conf = global_conf
        self.image_conf = image_conf
        self.setWindowTitle("Programmable-Image Viewer")
        wsizex = self.global_conf.get("wsizex", 300)
        wsizey = self.global_conf.get("wsizey", 300)
        self.resize(wsizex, wsizey)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        win_w, win_h = self.width(), self.height()
        sizex = self.global_conf.get("sizex", 6)
        sizey = self.global_conf.get("sizey", 6)
        # Размер ячейки для отрисовки
        cell_w = win_w / sizex
        cell_h = win_h / sizey

        # Рисуем по рядам (номер ряда начинается с 1)
        for row in sorted(self.image_conf.keys()):
            y = (row - 1) * cell_h
            x = 0
            for seg in self.image_conf[row]:
                # Для GUI ожидается, что цвет задаётся либо как rgba(...), либо как имя.
                col_str = seg["color"]
                if col_str.upper() in ["BLACK", "WHITE", "RED", "GREEN", "BLUE", "YELLOW", "CYAN", "MAGENTA"]:
                    # Используем простое соответствие (опционально можно расширить)
                    color_names = {
                        "BLACK": (0, 0, 0, 255),
                        "WHITE": (255, 255, 255, 255),
                        "RED": (255, 0, 0, 255),
                        "GREEN": (0, 255, 0, 255),
                        "BLUE": (0, 0, 255, 255),
                        "YELLOW": (255, 255, 0, 255),
                        "CYAN": (0, 255, 255, 255),
                        "MAGENTA": (255, 0, 255, 255)
                    }
                    rgba = color_names.get(col_str.upper(), (0, 0, 0, 255))
                else:
                    rgba = parse_rgba(col_str)
                qt_color = QtGui.QColor(*rgba[:3])
                painter.setBrush(qt_color)
                painter.setPen(QtCore.Qt.NoPen)
                pix_w = cell_w * seg["multiplier"]
                painter.drawRect(int(x), int(y), int(pix_w), int(cell_h))
                x += pix_w

def main():
    if not args.filename.endswith(".pimg"):
        print(Fore.RED + "Error: Unsupported file format!" + Style.RESET_ALL)
        sys.exit(1)

    global_conf, image_conf = parse_config(args.filename)

    t = global_conf.get("t")
    # Режимы CLI: "c" и "c_o" (CLI и CLI-old)
    if t in ("c", "c_o"):
        print_image_cli(image_conf, mode=t)
    # Режим GUI
    elif t == "g":
        app = QtWidgets.QApplication(sys.argv)
        window = ImageWidget(global_conf, image_conf)
        window.show()
        sys.exit(app.exec_())
    else:
        print(Fore.RED + "Error: Unknown mode. Use t='g' for GUI, 'c' for CLI, or 'c_o' for CLI-old." + Style.RESET_ALL)
        sys.exit(1)

if __name__ == "__main__":
    main()
