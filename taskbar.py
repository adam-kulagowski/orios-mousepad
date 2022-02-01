#!/usr/bin/python3

import wx.adv
import wx
import dbus
import threading
import time
import os
import configparser

config_file="orios_pad.ini"

TRAY_TOOLTIP = 'Orios Mousepad' 
TRAY_ICON = 'icon_dark_64.png' 
vid = "0C45"	# Change it for your device
pid = "763D"	# Change it for your device

MODES = {"Swirl": 0, "Neon": 1, "Breath": 2, "Fillup": 5, "Round":  6, "Flow": 7, "Left-Right": 8, "Off": 9}
COLORS = {"Red": 0 , "Orange": 1, "Yellow": 2, "Green": 3, "Cyan": 4, "Blue": 5, "Violet": 6, "White": 7, "None": 99} 

stop_thread = False


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

def screen_lock():
    global CUR_MODE
    global CUR_COL
    global OLD_MODE
    global OLD_COL
    global stop_threads

    session_bus = dbus.SessionBus()
    screensaver_list = ['org.gnome.ScreenSaver',
                    'org.cinnamon.ScreenSaver',
                    'org.kde.screensaver',
                    'org.freedesktop.ScreenSaver']
    for each in screensaver_list:
        try:
            object_path = '/{0}'.format(each.replace('.', '/'))
            get_object = session_bus.get_object(each, object_path)
            get_interface = dbus.Interface(get_object, each)
            status = bool(get_interface.GetActive())        
            environment=each
            break
        except dbus.exceptions.DBusException:
            pass
    
    old_status=False
    
    # Not ideal - we should subscribe to dbus events instead of pooling
    while [ 1 ]:
        object_path = '/{0}'.format(environment.replace('.', '/'))
        get_object = session_bus.get_object(each, object_path)
        get_interface = dbus.Interface(get_object, each)
        status = bool(get_interface.GetActive())        
        if old_status==False and status==True:
            OLD_MODE = CUR_MODE
            OLD_COL = CUR_COL
            set_mode(9)
        elif old_status==True and status==False:
            #print(OLD_MODE,OLD_COL)
            set_mode(OLD_MODE,OLD_COL)

        old_status=status
        #print(status)
        time.sleep(1)
        
        if stop_thread:
            print("Exit")
            break

def create_menu_item(menu, label, func):
    global CUR_MODE
    global CUR_COL

    if label in MODES and MODES[label]==CUR_MODE:
        item = wx.MenuItem(menu, -1, label, "", wx.ITEM_CHECK)
    elif label in COLORS and COLORS[label]==CUR_COL:
        item = wx.MenuItem(menu, -1, label, "", wx.ITEM_CHECK)
    else:
        item = wx.MenuItem(menu, -1, label)
        
    menu.Bind(wx.EVT_MENU, func, id=item.GetId())
    menu.Append(item)

    if item.IsCheckable():
        item.Check()

    return item


def set_mode(mode,color=99):

    global CUR_MODE
    global CUR_COL

    CUR_MODE=mode
    CUR_COL=color

    rootdir="/sys/class/hidraw/"
    
    #we search for hidraw that is assigned to VID:PID
    for subdir,dirs,files in os.walk(rootdir):
        for dir in dirs:
            mousepad_dev=0
            f=open(rootdir+dir+"/device/uevent",'r')
            lines=f.readlines()
            for line in lines:
                line_s=line.strip().split("=")
                if line_s[0] == "HID_ID" and line_s[1] == "0003:0000"+vid+":0000"+pid:
                    mousepad_dev=1
                if line_s[0] == "HID_PHYS" and line_s[1][-6:] == "input1" and mousepad_dev == 1:
                    device=dir
            f.close()

    dev = open("/dev/"+device, 'wb+')  
    start_packet(dev)

    packet = bytearray(MODE_PKT)
    packet[8] = mode
    checksum = sum(packet[FIRST_DATA_NDX:])
    set_16_bit(packet, CHECKSUM_NDX, checksum)
    dev.write(packet)
    dev.flush()
    d = dev.read(64)

    if mode==3:
        packet = bytearray(COL_PKT)
        packet[9] = color
        checksum = sum(packet[FIRST_DATA_NDX:])
        set_16_bit(packet, CHECKSUM_NDX, checksum)
        dev.write(packet)
        dev.flush()
        d = dev.read(64)

    finish_packet(dev)
    dev.close()

def on_swirl(self):
    set_mode(0)
def on_neon(self):
    print ('on_neon')
    set_mode(1)
def on_breath(self):
    print ('on_breath')
    set_mode(2)
def on_fillup(self):
    print ('on_fillup')
    set_mode(5)
def on_round(self):
    print ('on_round')
    set_mode(6)
def on_flow(self):
    print ('on_flow')
    set_mode(7)
def on_left_right(self):
    print ('on_left_right')
    set_mode(8)
def on_off(self):
    print ('on_off')
    set_mode(9)
def on_static_red(self):
    print ('on_static_red')
    set_mode(3,0)
def on_static_orange(self):
    print ('on_static_orange')
    set_mode(3,1)
def on_static_yellow(self):
    print ('on_static_yellow')
    set_mode(3,2)
def on_static_green(self):
    print ('on_static_green')
    set_mode(3,3)
def on_static_cyan(self):
    print ('on_static_cyan')
    set_mode(3,4)
def on_static_blue(self):
    print ('on_static_blue')
    set_mode(3,5)
def on_static_violet(self):
    print ('on_static_violet')
    set_mode(3,6)
def on_static_white(self):
    print ('on_static_white')
    set_mode(3,7)


#def on_hello():
#    print ('Hello, world!')

class TaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)

        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def CreatePopupMenu(self):
        menu = wx.Menu()

        #for effect in ['swirl', 'neon', 'breath', 'static', 'fillup', 'round', 'flow', 'left-right', 'off']:
        create_menu_item(menu, "Swirl", on_swirl)
        create_menu_item(menu, "Neon", on_neon)
        create_menu_item(menu, "Breath", on_breath)
        create_menu_item(menu, "Fillup", on_fillup)
        create_menu_item(menu, "Round", on_round)
        create_menu_item(menu, "Flow", on_flow)
        create_menu_item(menu, "Left-Right", on_left_right)
        create_menu_item(menu, "Off", on_off)
        menu.AppendSeparator()
        submenu = wx.Menu()
        menu.Append(wx.ID_ANY, 'Color', submenu)
        create_menu_item(submenu, "Red", on_static_red)
        create_menu_item(submenu, "Orange", on_static_orange)
        create_menu_item(submenu, "Yellow", on_static_yellow)
        create_menu_item(submenu, "Green", on_static_green)
        create_menu_item(submenu, "Cyan", on_static_cyan)
        create_menu_item(submenu, "Blue", on_static_blue)
        create_menu_item(submenu, "Violet", on_static_violet)
        create_menu_item(submenu, "White", on_static_white)                
        menu.AppendSeparator()
        create_menu_item(menu, 'Exit', self.on_exit)
        return menu

    def set_icon(self, path):
        icon = wx.Icon(path)
        self.SetIcon(icon, TRAY_TOOLTIP)

    #left click switches mousepad between off/last mode
    def on_left_down(self, event):
        global CUR_MODE
        global CUR_COL
        global OLD_MODE
        global OLD_COL

        if CUR_MODE != 9:
            OLD_MODE = CUR_MODE
            OLD_COL = CUR_COL
            set_mode(9,0)
        else:
            set_mode(OLD_MODE,OLD_COL)

    def on_exit(self, event):
        global CUR_MODE
        global CUR_COL
        global OLD_MODE
        global OLD_COL
        global stop_thread
        stop_thread = True

        config = configparser.ConfigParser()
        config['ORIOS'] = {}
        config['ORIOS']['cur.mode'] = str(CUR_MODE)
        config['ORIOS']['cur.col'] = str(CUR_COL)
        config['ORIOS']['old.mode'] = str(OLD_MODE)
        config['ORIOS']['old.col'] = str(OLD_COL)
        with open(config_file, 'w') as configfile:
            config.write(configfile)

        wx.CallAfter(self.Destroy)
        self.frame.Close()

class App(wx.App):
    def OnInit(self):
        frame=wx.Frame(None)
        self.SetTopWindow(frame)
        TaskBarIcon(frame)
        return True

def main():
    global CUR_MODE
    global CUR_COL
    global OLD_MODE
    global OLD_COL

    config = configparser.ConfigParser()
    config.read(config_file)
    if "ORIOS" in config.sections():
        CUR_MODE=int(config['ORIOS']['cur.mode'])
        CUR_COL=int(config['ORIOS']['cur.col'])
        OLD_MODE=int(config['ORIOS']['old.mode'])
        OLD_COL=int(config['ORIOS']['old.col'])
    else:
        CUR_MODE=0
        CUR_COL=0
        OLD_MODE=0
        OLD_COL=0

    x = threading.Thread(target=screen_lock)
    x.start()
    set_mode(CUR_MODE,CUR_COL)
    app = App(False)
    app.MainLoop()


if __name__ == '__main__':
    main()
