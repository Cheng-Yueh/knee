import smbus

I2C_HANDLE_DICT = {} # {dev_add: handle_no}
PCF8591_ADD = 0x48
MODE = 0b01000100


def set_mode(auto_inc = None, channel = None, PCF8591_add = PCF8591_ADD):
    
    # channel: None for all, 0-3 for one channel
    if channel in range(3): auto_inc = False
    
    global MODE
    bin_auto_inc = {True:4, False:0}.get(auto_inc, MODE & 0b100)
    bin_channel = {i:i for i in range(4)}.get(channel, MODE & 0b11)
    mode = 64 + bin_auto_inc + bin_channel # include analogue output
    bus.write_byte(PCF8591_add, mode)
    MODE = mode
    
    return mode


def get_adc_values(mode = MODE, n = 1, PCF8591_add = PCF8591_ADD):
    
    # returns a list of values
    bus.write_byte(PCF8591_add, mode)
    data = []
    for i in range(4**((mode & 0b100) >> 2)*n + 1):
        data.append(bus.read_byte(PCF8591_add))
    
    # flush first value
    return data[1:]

bus = smbus.SMBus(1)
