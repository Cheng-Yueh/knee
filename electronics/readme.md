# Electronics
Custom electronics were devised for driving this open source product. Two relevant PCBs are:
*	Joint angle sensor (ENCODER): acquires the absolute angular position of the knee using a Hall-effect IC.
*	Motors and solenoid driver (DRIVER_KNEE_V5): independently maintains constant actuation using built-in PWM functionality. Output current could be estimated on each of the four motor H-bridge channels.

Both devices are managed using I2C (SMBus) protocol. Get your PCB and solder mask made with files in [/GERBER](GERBER/). Reflow soldering is recommended for the surface mount devices. Advise processing bottom layer before top layer. Refer [soldering schematic PDF](Soldering%20Schematics.pdf).

Alternatively, modify and adapt the mechanical CAD model to suit your own electronics as you wish.

<img src="/assets/knee_PCB_iso_white_crop.jpg" alt="drawing"/>

## ICs used
The tables exclude passive or connector components.

### DRIVER_KNEE_V5
| IC name  | Description | Footprint | Quantity |
| ------------- | ------------- | - | - |
| PCA9685PW  | 16-channel, 12-bit PWM Fm+ I2C-bus LED controller  | TSSOP28 | 1 |
| PCF8591T  | 8-bit A/D and D/A converter  | SO16W | 1 |
| MC33932VW | 5.0 A throttle control H-bridge | HSOP44 | 2 |
| DRV8871-Q1 | 3.6-A Brushed DC Motor Driver With Internal Current Sense (PWM Control) | HSOP8 | 1 |
### ENCODER
| IC name  | Description | Footprint | Quantity |
| ------------- | ------------- | - | - |
| AS5048B  | Magnetic Rotary Encoder (14-Bit Angular Position Sensor) | TSSOP14 | 1 |

## DRIVER_KNEE_V5 wiring
Motor [wiring configuration](Wiring%20Configuration.pdf) is separately outlined, which is compatible with the Python code provided. Other connections are tabulated below.

| PCB label    | Connect to           | Component                 | Remarks                                      |
| ------------ | -------------------- | ------------------------- | -------------------------------------------- |
| M1 to M8     | Motor pins           | DC motors                 | Refer Wiring Configuration.pdf               |
| S1           | Red (+) wire         | Latching solenoid         | Refer manufacturer datasheet                 |
| S2           | Black (-) wire       | Latching solenoid         |                                              |
| VM           | 12: 24V<br>GND: ground | Power supply            | Intended for 12V but 24V compatible          |
| VDD          | 5: 5V<br>GND: ground |                           |                                              |
| U1A0 to U1A5 |                      | Jumpers                   | Programmable I2C slave address for PCA9685PW |
| U3A0 to U3A3 |                      | Jumpers                   | Programmable I2C slave address for PCF8591T  |
| SDA          | I2C data line        | Computer/ microcontroller |                                              |
| SCL          | I2C clock line       | Computer/ microcontroller |                                              |
| GND          | Ground               |                           | Common I2C and VM ground                     |

