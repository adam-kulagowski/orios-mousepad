#!/usr/bin/python


import time
import os
import binascii
import argparse
from codecs import encode
import csv

#vid = 0x0c45	# Change it for your device
#pid = 0x763d	# Change it for your device

PACKET_SIZE = 64

#Start and end packets w/ checksum coded in
START_PKT =        [0x04, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

FINISH_PKT =       [0x04, 0x02, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

#Template for config packet
# First LED is 
# 8th byte: RED
# 10th byte: BLUE
# 12th byte: GREEN
# Second LED is:
# 11th byte: RED
# 13th byte: BLUE
# 15th byte: GREEN
# Third LED is:
# 14th byte: RED
# 16th byte: BLUE
# 18th byte: GREEN
# etc
#There are 10 LEDs it total

LED_PKT =          [0x04, 0x00, 0x00, 0x12, 0x21, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

# value of 8th byte
# 0: swirl
# 1: neon
# 2: breath
# 3: static
# 4: freeze?
# 5: fillup
# 6: round
# 7: flow
# 8: left-right
# 9: off

MODE_PKT =         [0x04, 0x00, 0x00, 0x06, 0x01, 0x01, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

#must be after STATIC_RED mode
#nineth! byte: 3 last bits for RGB colors (no levels)
# 0 - red
# 1 - red+green (orange)
# 2 - red+green (yellow)
# 3 - green
# 4 - green+blue (cyan)
# 5 - blue
# 6 - red + blue (violet)
# 7 - white

COL_PKT =          [0x04, 0x00, 0x00, 0x06, 0x02, 0x08, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

CHECKSUM_NDX  = 1
FIRST_DATA_NDX = 3
FIRST_LED_NDX = 8
LED_SIZE = 3

def set_16_bit(packet, index, short):
    packet[index    ] =  short & 0x00ff
    packet[index + 1] = (short & 0xff00) >> 8

#sometimes when poking random bits into device, the mousepad became unresponsive. This packet was resting it.
def reset(dev):
    packet = bytearray(LED_PKT)
    packet[3] = 13
    packet[4] = 0x1
    checksum = sum(packet[FIRST_DATA_NDX:])
    set_16_bit(packet, CHECKSUM_NDX, checksum)
    dev.write(bytearray(packet))
    dev.flush()
    d = dev.read(64)

#set color&brighnes of specific LED in direct mode
def set_led(packet, index, rgb):
    #order is Red Blue Green - let fix it to Red Green Blue
    packet[FIRST_LED_NDX+index*3]=rgb[0]
    packet[FIRST_LED_NDX+index*3+2]=rgb[2]
    packet[FIRST_LED_NDX+index*3+4]=rgb[1]

#we should start talking to device w/ that packet
def start_packet(dev):
    packet = bytearray(START_PKT)
    dev.write(bytearray(packet))
    dev.flush()
    d = dev.read(64)

#we should end talking to device w/ that packet
def finish_packet(dev):
    packet = bytearray(FINISH_PKT)
    dev.write(bytearray(packet))
    dev.flush()
    d = dev.read(64)

#in direct mode we are controling each lead independly
#in order to do so we are using CSV file in format:
# HEADER, HEADER, HEADER,....
# delay(MS), Led1 Red, Led1 Green, Led1 Blue, Led2 Red, Led2 Green, Led2 Blue, Led3 Red, Led3 Green, Led3 Blue ... Led10 Red, Led10 Green, Led10 Blue 
# delay(MS), Led1 Red, Led1 Green, Led1 Blue, Led2 Red, Led2 Green, Led2 Blue, Led3 Red, Led3 Green, Led3 Blue ... Led10 Red, Led10 Green, Led10 Blue 
# delay(MS), Led1 Red, Led1 Green, Led1 Blue, Led2 Red, Led2 Green, Led2 Blue, Led3 Red, Led3 Green, Led3 Blue ... Led10 Red, Led10 Green, Led10 Blue 
# etc
# we are loading that file, skippng first line, the for each line we wait 'delay' value then
# we set each LED color accordingly
# then we are going to the next line...
# after reaching the end of file we go to the beggining

def mode_direct(args):
    print("Opening the device")
    #based on dmesg
    dev = open(args.device, 'wb+')

    start_packet(dev)

    csvfile =  open(args.csv, 'r')
    raw_arr = csv.reader(csvfile, delimiter=',', quotechar='"')
    header = next(raw_arr)
    #convert str to int
    int_arr = []
    for row in raw_arr:
        row=list(map(int,row))
        int_arr = int_arr + [ row ]

    try:
        print("Press Ctrl-C to terminate while statement")
        while True:
            for row in int_arr:
                time.sleep(row[0]/1000)
                i=0
                it = iter(row[1:])
                rgb_row = zip(it, it, it)
                packet = bytearray(LED_PKT)
                for r,g,b in rgb_row:
                    set_led(packet, i, [r,g,b])
                    i=i+1
                checksum = sum(packet[FIRST_DATA_NDX:])
                set_16_bit(packet, CHECKSUM_NDX, checksum)
                dev.write(bytearray(packet))
                dev.flush()
                d = dev.read(64)

    except KeyboardInterrupt:
        finish_packet(dev)
        pass

    print("Closing the device")
    dev.close()

    print("Done")

#in mode auto we set predefined mode and we exit the program
#in order to set static color (third mode) a second packet is needed.
def mode_auto(args):
    print("Opening the device")
    #based on dmesg
    dev = open(args.device, 'wb+')

    start_packet(dev)

    packet = bytearray(MODE_PKT)
    packet[8] = args.mode
    checksum = sum(packet[FIRST_DATA_NDX:])
    set_16_bit(packet, CHECKSUM_NDX, checksum)
    dev.write(packet)
    dev.flush()
    d = dev.read(64)

    if args.mode==3:
        packet = bytearray(COL_PKT)
        packet[9] = args.color
        checksum = sum(packet[FIRST_DATA_NDX:])
        set_16_bit(packet, CHECKSUM_NDX, checksum)
        dev.write(packet)
        dev.flush()
        d = dev.read(64)

    finish_packet(dev)

    print("Closing the device")
    dev.close()

    print("Done")




# Create the parser
parser = argparse.ArgumentParser(description='Control ORIOS RGB mousepad')

required_arg = parser.add_argument_group('Required arguments')
required_arg.add_argument('-d',
                       metavar='device',
                       dest="device",
                       type=str,
                       help='The hidraw device in form of /dev/hidrawX',
                       required=True)


subparsers = parser.add_subparsers(help='mode of operation')
parser_a = subparsers.add_parser(name="auto")
parser_a.set_defaults(func=mode_auto)
parser_a.add_argument('-m',
                       metavar='mode',
                       dest="mode",
                       type=int,
                       choices=[0,1,2,3,5,6,7,8,9],
                       default=1,
                       help='Light scheme {0: swirl, 1: neon (default), 2: breath, 3: static, 5: fillup, 6: round, 7: flow, 8: left-right, 9: off}')


parser_a.add_argument('-c',
                       metavar='color',
                       dest="color",
                       type=int,
                       default=0,
                       choices=[0,1,2,3,4,5,6,7],
                       help='Color for static mode: {0: red (default), 1: orange, 2: yellow, 3: green, 4: cyan, 5: blue, 6: violet, 7:white}')

#ex_group = parser.add_mutually_exclusive_group()
parser_b = subparsers.add_parser(name="direct")
parser_b.set_defaults(func=mode_direct)
parser_b.add_argument('-f',
                       metavar='file',
                       dest="csv",
                       type=str,
                       help='The location of CSV file w/ direct mode instructions')



# Execute the parse_args() method
args = parser.parse_args()

#print(args)
args.func(args)