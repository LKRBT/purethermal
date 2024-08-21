# PureThermal

## Install
```bash
$ git clone https://github.com/groupgets/libuvc
$ sudo apt-get install cmake -y
$ sudo apt-get install libusb-1.0-0-dev
$ sudo apt-get install libjpeg-dev -y

$ cd libuvc
$ mkdir build
$ cd build
$ cmake ..
$ make && sudo make install

$ sudo ldconfig -v
$ cd ../

$ lsusb
-----------------------
    Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
    Bus 001 Device 003: ID 1e4e:0100 Cubeternet WebCam
    Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub
    Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub

$ sudo nano /etc/udev/rules.d/99-usb.rules
# add following sentence
    SUBSYSTEM=="usb", ATTR{idVendor}=="1e4e", ATTR{idProduct}=="0100", MODE="0666"

$ sudo udevadm control --reload-rules
$ sudo udevadm trigger
```
## Ref.
https://medium.com/@soorajece1993/purethermal-2-flir-lepton-3-5-interfacing-python-16f511349947

https://github.com/groupgets/libuvc

https://github.com/soorajsknair93/PureThermal2-FLIR-Lepton3.5-Interfacing-Python

https://github.com/groupgets/purethermal1-uvc-capture