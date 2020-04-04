#!/usr/bin/env bash
cd /var/tmp;
wget 'http://www.imagemagick.org/download/ImageMagick.zip';
unzip ImageMagick.zip;
cd ImageMagick.zip;
./configure;
make;
make install;
cd ..;
apt-get install libboost-all-dev -y;
apt-get install build-essential checkinstall && apt-get build-dep imagemagick -y;
wget 'http://www.imagemagick.org/download/python/PythonMagick-0.9.12.zip';
unzip PythonMagick-0.9.12.zip;
cd PythonMagick-0.9.12.zip
./configure;
make;
make install;
pip2 install boost-python;
