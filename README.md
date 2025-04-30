# P-IMG project
## This is programmable images project
# Usage:
Flags:
-c; --cli - render image in console
-f; --filename - filename
# Example:
## Linux:
```sh
./p-img.sh -f "example1.pimg"
```
## Windows:
```ps
./p-img.bat -f "example1.pimg"
```
# Prerequireties:
- Python3
- py3: PyQt5
- py3: colorama
- py3: os
- py3: sys
- py3: argparse
- py3: re
# Installation:
## Linux (/bin ln method):
Just type these commands in order:
```sh
git clone https://github.com/Se1d228/p-img
cd p-img
sudo cp p-img.sh /bin/
sudo cp p-img.py /bin/
sudo cp logo.png /bin/
sudo ln -s /bin/p-img.sh /bin/p-img
chmod +x /bin/p-img.sh
```
## Linux (/usr/local/bin if /bin is RO):
Do exactly same as in /bin method, but replace "/bin" with "/usr/local/bin"
## Linux (bash.bashrc method):
1. Clone this repository:
```sh
git clone https://github.com/Se1d228/p-img
```
2. Remember your git clonned directory (I will mark it as ```/path/to/p-img```) and start edit ~/.bashrc file trough ```sudo vi ~/.bashrc``` or ```sudo nano ~/.bashrc``` and write following line to file:
```bash
alias p-img="/path/to/p-img.sh"
```
## Windows:
1. type this in CMD:
```ps
git clone https://github.com/Se1d228/p-img
```
2. Create shortcut for p-img.bat. Name it "p-img"
3. Put this shortcut in ```C:\Windows\System32```
Now you can run it with "p-img <args>" trough CMD or Win+R menu
# Notes:
1. CLI mode is not fully tested yet, run ```p-img -c -f example2.pimg``` to open CLI images
---
P-IMG project © 2025 by Se1d228 is licensed under CC BY-NC-SA 4.0
