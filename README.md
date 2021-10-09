# Speedlink ORIOS RGB Gaming Mouse-pad

The ORIOS mouse pad is quite a nice piece of hardware if someone is looking for cheap, hard mouse-pad w/ RGB lightening. It has multiple hard coded modes controlled via touch button and also can be controlled via Windows software. It is however lacking Linux support.

This simple python program allows to control above device from the CLI.

Product page is located here:
<https://www.speedlink.com/en/ORIOS-RGB-Gaming-Mousepad-black/SL-620100-BK>

## Device presence

Upon connection the device register itself as a HID device:

``` bash
fidor@Fidor-pc:~/github/mousepad$ dmesg
[...]
[2551219.470083] usb 1-5.2: new full-speed USB device number 51 using xhci_hcd
[2551219.572101] usb 1-5.2: New USB device found, idVendor=0c45, idProduct=763d, bcdDevice= 1.02
[2551219.572102] usb 1-5.2: New USB device strings: Mfr=1, Product=2, SerialNumber=0
[2551219.572103] usb 1-5.2: Product: USB DEVICE
[2551219.572103] usb 1-5.2: Manufacturer: SONiX
[2551219.580771] input: SONiX USB DEVICE as /devices/pci0000:00/0000:00:14.0/usb1/1-5/1-5.2/1-5.2:1.0/0003:0C45:763D.004B/input/input196
[2551219.638436] hid-generic 0003:0C45:763D.004B: input,hidraw0: USB HID v1.11 Keyboard [SONiX USB DEVICE] on usb-0000:00:14.0-5.2/input0
[2551219.639538] input: SONiX USB DEVICE Keyboard as /devices/pci0000:00/0000:00:14.0/usb1/1-5/1-5.2/1-5.2:1.1/0003:0C45:763D.004C/input/input197
[2551219.698236] input: SONiX USB DEVICE Wireless Radio Control as /devices/pci0000:00/0000:00:14.0/usb1/1-5/1-5.2/1-5.2:1.1/0003:0C45:763D.004C/input/input198
[2551219.698363] input: SONiX USB DEVICE Consumer Control as /devices/pci0000:00/0000:00:14.0/usb1/1-5/1-5.2/1-5.2:1.1/0003:0C45:763D.004C/input/input199
[2551219.698457] input: SONiX USB DEVICE as /devices/pci0000:00/0000:00:14.0/usb1/1-5/1-5.2/1-5.2:1.1/0003:0C45:763D.004C/input/input200
[2551219.698646] hid-generic 0003:0C45:763D.004C: input,hiddev0,hidraw1: USB HID v1.11 Keyboard [SONiX USB DEVICE] on usb-0000:00:14.0-5.2/input1
```

Two devices are created. In this case:

``` bash
fidor@Fidor-pc:~/github/mousepad$ ls -l /dev/hidraw*
crw-rw----+ 1 root root 240, 0 paź  9 20:24 /dev/hidraw0
crw-rw----+ 1 root root 240, 1 paź  9 20:24 /dev/hidraw1
[...]
```

The USB VID:PID is as follows:

``` bash
fidor@Fidor-pc:~/github/mousepad$ lsusb
[...]
Bus 001 Device 051: ID 0c45:763d Microdia
```

## Device description

The device contains 10 RGB led that are placed in the following way:

``` bash
                    |
2           1 //#########\\ 10          9
 /-----------/=============\-----------\
 |                  @         Speedlink|
 |                                     |
 |                                     |
 |                                     |
3|                                     |8
 |                                     |
 |                                     |
 |                                     |
 |  ORIOS                              |
 \_____________________________________/
 4           5               6           7
```

## Communication protocol

Device can be configured using 64B packets sent to second hidraw device (in above dmesg scenario it would be /dev/hidraw1). Based on reverse engineering, pure luck and brute force (as the Windows software supports only direct mode the second mode had to be detected manually) I was able to decrypt the following packets:

### Start packet

Fixed packet that should begin any communication towards the mouse-pad. Packet format is as follows:

``` c
0x04, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
```

### Finish packet

Fixed packet that should end any communication towards the mouse-pad. Packet format is as follows:

``` c
0x04, 0x02, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
```

### Modes of operation

There three modes of operation:

- auto mode: will switch mouse to one of predefined light mode
- direct mode: with each pack we will control each RGB led
- sniffer mode: mouse-pad will report to us of its current light status (direct mode in reverse) - not yet supported

#### Auto mode

##### Mode packet

This packet set one of the light modes that is available via touch button on the mouse-pad:

``` c
0x04, 0x00, 0x00, 0x06, 0x01, 0x01, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
```

The value of 9th byte (8th counting from 0) can be one of the following value:

- 0: rainbow swirl (swirl)
- 1: color cycling (neon)
- 2: breathing color cycling (breath)
- 3: static color (needs followup color packet )
- 4: Unused - freezes the mouse-pad
- 5: rainbow colors will light up all leds from left to right (fillup)
- 6: rainbow color will travel around the mouse-pad (round)
- 7: mouse-pad will cycle from all RGB spectrum, however only two color will be shown at one moment (flow)
- 8: rainbow colors will travel from left to right and return (left-right)
- 9: off

Note that this is not a fixed packet the second and third bytes will change their value as they are used for checksum.

##### Color packet

This packet should be sent in case of mode set to 3: static color:

``` c
0x04, 0x00, 0x00, 0x06, 0x02, 0x08, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
```

In this case a color value is encoded on tenth (9th counting from 0) byte and it can take the following values:

- 0: red
- 1: red+green (orange)
- 2: red+green (yellow)
- 3: green
- 4: green+blue (cyan)
- 5: blue
- 6: red + blue (violet)
- 7: white

Note that this is not a fixed packet the second and third bytes will change their value as they are used for checksum.

#### Direct mode

##### Direct packet

This packet must be sent at least every second. Otherwise the mouse-pad will reset itself to last mode:

``` c
0x04, 0x00, 0x00, 0x06, 0x02, 0x08, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
```

From 9th byte (8th counting from 0) the individual LED are coded in Reg Blue Green. However there is one byte space between each color. The next LED starts from 12th (11th when counting from 0). This gives us (each index is counted from 0);

First LED is :

- 8th byte: RED
- 10th byte: BLUE
- 12th byte: GREEN

Second LED is:

- 11th byte: RED
- 13th byte: BLUE
- 15th byte: GREEN

Third LED is:

- 14th byte: RED
- 16th byte: BLUE
- 18th byte: GREEN
etc

There are 10 LEDs it total.

Note that this is not a fixed packet the second and third bytes will change their value as they are used for checksum.

## Possible compatible devices

This is based on similarities in design that devices below share with ORIOS mouse-pad. They might be working or not. If you own one of those devices please give a feedback:

#### Redragon P011 Orion RGB Mousepad

<https://www.redragonzone.com/products/redragon-p011-rgb-gaming-mouse-pad>

#### Ajazz AJPad RGB Hard Gaming Mouse Pad

<https://loftee.unicart2u.co/gaming-accessories/ajazz-ajpad-rgb-hard-gaming-mouse-pad>

##### Cooler Master RGB Hard Gaming Mousepad - MPA-MP720

<https://www.coolermaster.com/catalog/peripheral/mouse-pads/rgb-hard-gaming-mouse-pad/>

Unfortunately I cannot confirm this 100% as those vendors do not provide software for their mouse-pads (so maybe in order to save 1c they dropped data cable in favor for power only). However the build design are striking similar. So if someone has one of above mouse pad - could they confirm/deny my assumptions?

# No Warranty

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/gpl.html>

# Application usage

``` bash
fidor@Fidor-pc:~/github/mousepad$ ./mousepad_openrgb.py -h
usage: mousepad_openrgb.py [-h] -d device {auto,direct} ...

Control ORIOS RGB mousepad

positional arguments:
  {auto,direct}  mode of operation

optional arguments:
  -h, --help     show this help message and exit

Required arguments:
  -d device      The hidraw device in form of /dev/hidrawX
fidor@Fidor-pc:~/github/mousepad$ ./mousepad_openrgb.py auto -h
usage: mousepad_openrgb.py auto [-h] [-m mode] [-c color]

optional arguments:
  -h, --help  show this help message and exit
  -m mode     Light scheme {0: swirl, 1: neon (default), 2: breath, 3: static,
              5: fillup, 6: round, 7: flow, 8: left-right, 9: off}
  -c color    Color for static mode: {0: red (default), 1: orange, 2: yellow,
              3: green, 4: cyan, 5: blue, 6: violet, 7:white}
fidor@Fidor-pc:~/github/mousepad$ ./mousepad_openrgb.py direct -h
usage: mousepad_openrgb.py direct [-h] [-f file]

optional arguments:
  -h, --help  show this help message and exit
  -f file     The location of CSV file w/ direct mode instructions
```

The application support two modes:

- auto: when user can set one of predefined modes described earlier
- direct: when user can control each lead via prepared CSV file

There is no auto detection so user must provide `-d` argument pointing to `/dev/hidrawX` file used by mouse-pad.

## CSV file format

Since in in direct mode we are controlling each lead independently, so in order to do so we had to provide CSV file contains values for each RGB LED. The format of CSV is as follow:

``` csv
HEADER delay, HEADER R1, HEADER G1, HEADER B1, ....
delay(MS), Led1 Red, Led1 Green, Led1 Blue, Led2 Red, Led2 Green, Led2 Blue, Led3 Red, Led3 Green, Led3 Blue ... Led10 Red, Led10 Green, Led10 Blue 
delay(MS), Led1 Red, Led1 Green, Led1 Blue, Led2 Red, Led2 Green, Led2 Blue, Led3 Red, Led3 Green, Led3 Blue ... Led10 Red, Led10 Green, Led10 Blue 
delay(MS), Led1 Red, Led1 Green, Led1 Blue, Led2 Red, Led2 Green, Led2 Blue, Led3 Red, Led3 Green, Led3 Blue ... Led10 Red, Led10 Green, Led10 Blue 
[...]
```

Notes:

- delay should be in range 10-1000
- LEAD value should be in range 0-255

We are loading that file, skipping first line and proceed as below:

1. the for each line we wait 'delay' value in ms
2. we set each LED color accordingly
3. then we are going to the next line and repeat 1,2 steps
4. after reaching the end of file we go to the beginning

There two files provided as an example:

- red-sinus.csv - where we control the RED color of first and last LED
- white-walk.csv - where we light each led in white color for one second