# Games.Ordz

# Tried to build with nuitka but it was a failure
build on docker
https://medium.com/dazn-tech/nuitka-python3-and-scratch-4ce209ed6dd6


```bash
#!/bin/sh

python3.11 -m nuitka --standalone --plugin-enable=pylint-warnings --clang --prefer-source-code --warn-implicit-exceptions --follow-imports --prefer-source-code --warn-unusual-code  --output-dir=dist --include-data-dir='./lib/dat=./lib/dat' main.py
ex1="$PWD/enp/lib/python3.11/site-packages/numpy"
rsync -av --exclude=$ex1 "$PWD/enp/lib/python3.11/site-packages/" "$PWD/dist/main.dist/"

./dist/main.dist/main.bin
```
# setup now
1.
`enp/bin/python -m pip freeze | grep -vE '^(pyobjc-|pyobjc).*==' | awk '{print $1}' > requirements.txt`

turn on the local vpn with local port
for example if the system vpn URL or sock is to be
http://127.0.0.1:7890
then the port number will be 7890
if the vpn port is http://127.0.0.1:7891
then the port number will be 7891

## setup the system environment use local environments
Have the python 3.11 install on the system first and install the required packages with this command.
`pip install -r requirements.txt`

## start the service with this

`python3 main.py`

## other options

INPUTS. EXCEL file
address and private keys

NUMBERS. XX
how many local workers you would prefer

## version logs
======================
v0.2 - add vpn port and debug notice
v0.1 - Skygate v1
