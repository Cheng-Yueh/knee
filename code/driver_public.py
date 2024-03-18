import smbus, time, threading

# Registers/etc:
#PCA9685_ADDRESS    = 0x40
MODE1              = 0x00
MODE2              = 0x01
SUBADR1            = 0x02
SUBADR2            = 0x03
SUBADR3            = 0x04
PRESCALE           = 0xFE

LED_LIST = [i for i in range(6,67,4)]

ALL_LED_ON_L       = 0xFA
ALL_LED_ON_H       = 0xFB
ALL_LED_OFF_L      = 0xFC
ALL_LED_OFF_H      = 0xFD

# MODE 1 bits
RESTART            = 0x80
SLEEP              = 0x10
ALLCALL            = 0x01

# MODE 2 bits
INVRT              = 0x10
OUTDRV             = 0x04

MOTOR_ALLCALL_ADD = 0x70
MOTOR_PAIR_NO = 0


def motor_reg_id(motor_pair_no, driver = 0):
    
    # int 0 to 3
    # Returns register adress tuple for motor pair (Dn, IN1n, IN2n)
    # (M1, M2), (M3, M4), (M5, M6), (M7, M8) IN THIS ORDER!

    # Identify the first address of 4 registers per LED PWM
    if driver is 0:
        motor_reg_dic = {0: (LED_LIST[15], LED_LIST[0], LED_LIST[1]),
                         1: (LED_LIST[2], LED_LIST[13], LED_LIST[14]),
                         2: (LED_LIST[12], LED_LIST[3], LED_LIST[4]),
                         3: (LED_LIST[5], LED_LIST[10], LED_LIST[11]),
                         4: (None, LED_LIST[8], LED_LIST[7])}
    if driver is 1:
        motor_reg_dic = {key: value for (key, value) in
                         [(3-i,(None, LED_LIST[i*2], LED_LIST[i*2+1])) for i in range(4)]}
    
    return motor_reg_dic.get(motor_pair_no, None)


def solenoid_reg_id():
    
    # Returns register adress tuple for solenoid pair
    # (S_IN1, S_IN2)
    
    return motor_reg_id(4)[1:]


def set_PWM_freq(PCA9685_add, freq):
    
    # freq in Hz
    # bound between 0x03 (1526 Hz) and 0xFF (24 Hz)
    prescaleval = max(0x03, min(0xFF, int(25000000.0/(4096.0 * freq) - 1.0)))
    
    # sleep first before updating prescaler
    oldmode = bus.read_byte_data(PCA9685_add, MODE1)
    newmode = (oldmode & 0x7F) | 0x10    # sleep
    bus.write_byte_data(PCA9685_add, MODE1, newmode)  # go to sleep
    
    # update prescaler
    bus.write_byte_data(PCA9685_add, PRESCALE, prescaleval) 
    
    # wake + reinstate mode before sleep
    bus.write_byte_data(PCA9685_add, MODE1, oldmode)
    time.sleep(0.005) # SLEEP = 0 for min 500 us before RESTART bit = 1
    bus.write_byte_data(PCA9685_add, MODE1, oldmode | 0x80) # restart with orig LED vals
    
    return None


def write_LED_data(PCA9685_add, reg_add, led_times):
    
    # reg_add = address of first register address of relevant LED port
    # led_on, led_off = 0 to 4096 inclusive
    (led_on, led_off) = led_times
    bit_str = led_off << 16 | led_on
    data_list = []
    
    for i in range(4):
        data_list.append(bit_str & 0b11111111)
        bit_str = bit_str >> 8
    
    try_count = 0
    while try_count < 50:
        try:
            bus.write_i2c_block_data(PCA9685_add, reg_add, data_list)
            break
        except: try_count += 1

    return None


def set_motor(PCA9685_add, motor_pair_no, mode, duty, direction, delay = 0, disable = 0, driver = 0):
    
    # Modes when PWM is low:
    # 0: Brake low side slow decay
    # 1: Coast high-z
    # direction: 0 forward, 1 reverse
    # duty: 0.0 to 1.0 float
    # delay: in ticks (0 to 4095)
    # driver: 0 for knee, 1 for hip clutch/optiplus
    
    (D_add, IN1_add, IN2_add) = motor_reg_id(motor_pair_no, driver)
    if D_add is not None: write_LED_data(PCA9685_add, D_add, [0, 4096][::-2*disable+1]) # Enable/disable
    
    [high_dur, low_dur] = [round(4096*i) for i in (duty, 1-duty)][::-2*mode+1]
    
    # Always start with LED_ON
    if duty == 0:
        write_LED_data(PCA9685_add, IN1_add, [0, 4096][::-2*mode+1])
        write_LED_data(PCA9685_add, IN2_add, [0, 4096][::-2*mode+1])
    elif 0 < duty <=1.0:
        if 0 < duty < 1.0: [on_time, off_time] = [delay, (delay + high_dur) % 4096]
        if duty == 1.0: [on_time, off_time] = [4096, 0][::-2*mode+1]
        write_LED_data(PCA9685_add, [IN1_add, IN2_add][mode ^ direction], [on_time, off_time]) # PWM this LED
        write_LED_data(PCA9685_add, [IN2_add, IN1_add][mode ^ direction], [0, 4096][::-2*mode+1]) # Fix the other LED   
    
    return None


def stop_knee(mode, PCA9685_add):
    
    for motor_pair_no in range(4): set_motor(PCA9685_add, motor_pair_no, mode, 0, 0)
    
    return None


def set_knee(PCA9685_add, func, duty, duty_max = 0.25, duty_lambda = 1, duration = None, mode = 0):
    
    # Function:
    # 0: Forward (bend knee)
    # 1: Reverse
    # 2: Gear up
    # 3: Gear down
    # duty_lambda: duty prescaler to reduce gear upwards force
    #              during forward or reverse operations
    
    duty = min(duty, duty_max)
    for motor_pair_no in range(4):
        direction = [motor_pair_no>=2, motor_pair_no<2, 0, 1][func]
        duty_scale = [[duty_lambda, 1][direction], 1][func>=2]
        set_motor(PCA9685_add, motor_pair_no, mode, duty_scale*duty, direction)
    
    # turn off motor after a while if duration is set
    if duration is not None:
        stop_motors = threading.Timer(duration, lambda: stop_knee(mode, PCA9685_add))
        stop_motors.start()
    
    return None


def set_solenoid(PCA9685_add, mode, duration=0.1, lock_duty = 1.0, unlock_duty = 0.5):
    
    # mode: 0 lock, 1 unlock
    # unlocking voltage must be below 8.0V; unrestricted locking voltage
    set_motor(PCA9685_add, 4, 0, [lock_duty, unlock_duty][mode], mode)
    stop_solenoid = threading.Timer(duration, lambda: set_motor(PCA9685_add, 4, 0, 0, 0))
    stop_solenoid.start()
    
    return None


def initialize(PCA9685_add):
    
    bus.write_byte_data(PCA9685_add, MODE1, 0b00100001) # MODE 1 default
    bus.write_byte_data(PCA9685_add, MODE2, 0b00001100) # MODE 2 default
    bus.write_byte_data(PCA9685_add, ALL_LED_ON_L, 0) # Turn all LEDs off
    bus.write_byte_data(PCA9685_add, ALL_LED_ON_H, 0) # Turn all LEDs off
    bus.write_byte_data(PCA9685_add, ALL_LED_OFF_L, 0) # Turn all LEDs off
    bus.write_byte_data(PCA9685_add, ALL_LED_OFF_H, 16) # Turn all LEDs off
    set_PWM_freq(PCA9685_add, 1526)
    
    return None


bus = smbus.SMBus(1)
