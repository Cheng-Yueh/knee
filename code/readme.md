# Code overview
The default electronics provided can be operated using a Raspberry Pi using the two Python files:
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


# Holy code
more stuff *italics* **bold font** and normal text
``monospace text``
and ````opoo````

### `initialize(PCA9685_add)`
Executes much more
