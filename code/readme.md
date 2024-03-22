# Code overview
The default electronics provided can be operated using a Raspberry Pi using these Python files:
* driver_public.py: drives the actuators (motors and latching solenoid).
* encoder.py: retrieves joint angle readings from AS5048B.
* pcf8591_public.py: retrieves raw ADC values for motor current estimation.

## Usage
Recommended function APIs are documented below; helper functions are not included.

### driver_public.py
#### `initialize(PCA9685_add)`
Initializes the PCA9685PW PWM IC with default settings.

Parameters
*	PCA9685_add(int): I2C address.

Returns None

#### `set_PWM_freq(PCA9685_add, freq)`
Sets the desired PWM frequency of PCA9685PW to drive H-bridges.

Parameters
*	PCA9685_add(int): I2C address.
*	freq(int): PWM frequency in Hz.

Returns None

#### `set_knee(PCA9685_add, func, duty, duty_max = 0.25, duty_lambda = 1, duration = None)`
Actuates the knee motors with specified mode of operation.

Parameters
*	PCA9685_add(int): I2C address.
*	func(int): knee joint operation mode. 0: flexion (bend knee); 1: extension; 2: disengage transmission; 3: engage transmission.
*	duty(float): PWM motor duty (0 to 1).
*	duty_max(float): maximum permissible PWM motor duty (0 to 1) regardless of duty(float).
*	duty_lambda(float): duty prescaler (0 to 1) to impart a net downward compound transmission gear force using differential PWM motor duties.
*	duration(float): operation time in seconds; motors will turn off after duration.

Returns None

#### `set_solenoid(PCA9685_add, mode, duration=0.1, lock_duty = 1.0, unlock_duty = 0.5)`
Actuates the latching solenoid knee lock.

Parameters
*	PCA9685_add(int): I2C address.
*	mode(int): 0: lock; 1: unlock.
*	duration(float): operation time in seconds; solenoid will turn off after duration.
*	lock_duty(float): lock mode PWM duty (0 to 1).
*	unlock_duty(float): unlock mode PWM duty (0 to 1).

Returns None

### encoder.py
#### `read_angle(output = 'bit', offset = 0, remap = True, enc_add = ENC_ADD)`
Returns the absolute knee joint angle.

Parameters
*	output(str): 'bit': returns angle in raw bit value; ‘deg’: returns angle in degrees; ‘rad’: returns angle in radians.
*	offset(float): returns the angle relative to a prescribed offset value.
*	remap(bool): True: remaps angle equivalent to -180° < value ≤ 180°.
*	enc_add(int): I2C address.

Returns int if output == ‘bit’, else float

### pcf8591_public.py
#### `set_mode(auto_inc = None, channel = None, PCF8591_add = PCF8591_ADD)`
Initializes the ADC scanning mode, and returns the associated configuration mode value.

Parameters
*	auto_inc(bool): True: sets ADC to automatically increment return values over each channel as defined in IC datasheet; False or None: disables ADC auto increment.
*	channel(int): sets a single ADC channel (0 to 3) for returning values. Refer to IC datasheet.
*	PCF8591_add(int): I2C address.

Returns int

#### `get_adc_values(mode = MODE, n = 1, PCF8591_add = PCF8591_ADD)`
Reads and returns ADC values.

Parameters
*	mode(int): ADC scanning mode configuration value.
*	n(int): number of times to read the ADC with defined mode.
*	PCF8591_add(int): I2C address.

Returns list
