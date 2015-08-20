#!/bin/bash

python setup.py build_ext --inplace --force

cd tests
ln -sf ../nefis.so

### test working
#python nefis_inquire.py
