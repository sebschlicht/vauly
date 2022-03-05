#!/bin/sh

# copy required files to dedicated vauly folder in $HOME
mkdir -p "$HOME/.vauly"
cp -p vauly.py "$HOME/.vauly/"
cp -p vault-unpack.yml "$HOME/.vauly/"

# create symlink for wrapper in user binaries folder
mkdir -p "$HOME/bin"
ln -sf "$HOME/.vauly/vauly.py" "$HOME/bin/vauly"
