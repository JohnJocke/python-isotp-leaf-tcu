# python-isotp-leaf-tcu
Python script to read and write Nissan Leaf TCU settings using `python-can-isotp`: https://can-isotp.readthedocs.io/en/latest/

The script `tcu_config.py` is an example for use with the Lawicel CANUSB. The CAN hardware interface can be easily changed to any interface supported by `python-can`.
Check supported interfaces here: https://python-can.readthedocs.io/en/stable/interfaces.html

## Usage

### Install dependencies
```
> pip install python-can[serial]
> pip install can-isotp
```

### Help
```
> python tcu_config.py
Description: Python script to read/write Nissan Leaf TCU configuration with python-can-isotp
This script is an example for use with Lawicel CANUSB (python-can slcanBus)

Read usage: python tcu_config.py <serial_port>
Read example: python tcu_config.py COM4

Write usage: python tcu_config.py <serial_port> <config_item> <value>
Write example: python tcu_config.py COM4 apn_name hologram

All writeable config items:
activation
vin
apn_dial
apn_user
apn_pass
apn_name
dns1
dns2
proxy
proxy_port
apn_connection_type
server_hostname
```

### Read all parameters
```
> python tcu_config.py COM4
Starting diagnostic session 0xC0
Diagnostic session established
Reading all config items:
Name: activation, Value: 1, Raw: 610401
Name: signal_level, Value: ANT:0,RECEPTION:31,ERRRATE:79
Name: vin, Value: JN1FAAZE0U00XXXXX
Name: apn_dial, Value: *99#
Name: apn_user, Value: zero
Name: apn_pass, Value: emission
Name: apn_name, Value: hologram
Name: dns1, Value: auto
Name: dns2, Value: auto
Name: proxy, Value:                                                                                                     
Name: proxy_port, Value:
Name: apn_connection_type, Value: IP
Name: server_hostname, Value: nissan-eu-dcm-biz.viaaq.eu
```

### Usage with opencarwings
When using opencarwings, you usually only need to change the following fields:
* activation (must be set to 1)
* apn_name (according to your SIM card provider)
* server_hostname (if using self-hosted opencarwings server)

## Known issues
Writing of the VIN code does not work currently. Error response (raw bytes): `7F3B12`

## References
This script is based on the great work by developerfromjokela: https://github.com/developerfromjokela/nissan-leaf-tcu/

