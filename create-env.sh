#!/bin/bash

apt install curl
#curl --proto '=https' https://sh.rustup.rs -sSf | sh
#source $HOME/.cargo/env

if [ x"$PYTHON" = x ]
then
PYTHON=`which python3`
fi

echo "Using python $PYTHON"

$PYTHON -m venv --without-pip venv
. venv/bin/activate

wget -O /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py
python /tmp/get-pip.py

python -m pip install setuptools
python -m pip install bleak

