import smbus
from math import pi as pi

ENC_ADD = 0x40

REG_ANG_1 = 0xFE
REG_ANG_2 = 0xFF
REG_I2C_SLAVE_ADD = 0x15
REG_PRO_CNTL = 0x03


def read_angle(output = 'bit', offset = 0, remap = True, enc_add = ENC_ADD):
	
    # output: 'bits' returns raw bit value 0-16383, deg or rad
    
    valid = False
    while not valid:
        try:
            ang_1, ang_2 = bus.read_byte_data(enc_add, REG_ANG_1), \
                           bus.read_byte_data(enc_add, REG_ANG_2)
            valid = True
        except IOError: valid = False
    
    bit_val = ((ang_1 << 6) + ang_2 - offset) % 2**14
    if remap: bit_val = (lambda x: x - 2**14 if x > 2**13 else x)(bit_val)
    
    return {'bit': bit_val,
            'deg': bit_val * 360/2**14,
            'rad': bit_val * 2*pi/2**14}.get(output, None)


def otp_address(check, enc_otp_cont, enc_old_add = ENC_ADD):
    
    # burns OTP subaddress
    # enc_otp_cont: 4 bit OTP programmable subaddress
    # READ DATASHEET THOROUGHLY BEFORE EXECUTING PROGRAM

    if check != 'holyroly': return None

    import time

    # Set new I2C slave address
    bus.write_byte_data(enc_old_add, REG_I2C_SLAVE_ADD, enc_otp_cont)

    # Enable special programming mode
    ENC_NEW_ADD = 0b1000000 | (enc_otp_cont << 2)
    bus.write_byte_data(ENC_NEW_ADD, REG_PRO_CNTL, 0xFD)
    time.sleep(0.01)

    # Enable automatic programming procedure
    bus.write_byte_data(ENC_NEW_ADD, REG_PRO_CNTL, 0x08)
    time.sleep(0.01)

    # Disable special programming mode
    bus.write_byte_data(ENC_NEW_ADD, REG_PRO_CNTL, 0x00)
    time.sleep(0.01)

    return None


bus = smbus.SMBus(1)