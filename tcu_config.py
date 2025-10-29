import isotp
import logging
import sys

from can.interfaces.slcan import slcanBus

config_items = [
    {"configId": 0x04, "fieldLength": 1, "type": 2, "fieldMaxLength": 1, "readOnly": False, "name": "activation"},
    {"configId": 0x09, "fieldLength": 20, "type": 3, "fieldMaxLength": 20, "readOnly": True, "name": "signal_level"},
    {"configId": 0x81, "fieldLength": 17, "type": 0, "fieldMaxLength": 17, "readOnly": False, "name": "vin"},
    {"configId": 0x10, "fieldLength": 128, "type": 1, "fieldMaxLength": 128, "readOnly": False, "name": "apn_dial"},
    {"configId": 0x11, "fieldLength": 128, "type": 1, "fieldMaxLength": 128, "readOnly": False, "name": "apn_user"},
    {"configId": 0x12, "fieldLength": 128, "type": 1, "fieldMaxLength": 128, "readOnly": False, "name": "apn_pass"},
    {"configId": 0x13, "fieldLength": 128, "type": 1, "fieldMaxLength": 128, "readOnly": False, "name": "apn_name"},
    {"configId": 0x14, "fieldLength": 128, "type": 1, "fieldMaxLength": 128, "readOnly": False, "name": "dns1"},
    {"configId": 0x15, "fieldLength": 128, "type": 1, "fieldMaxLength": 128, "readOnly": False, "name": "dns2"},
    {"configId": 0x16, "fieldLength": 128, "type": 1, "fieldMaxLength": 128, "readOnly": False, "name": "proxy"},
    {"configId": 0x17, "fieldLength": 128, "type": 1, "fieldMaxLength": 128, "readOnly": False, "name": "proxy_port"},
    {"configId": 0x18, "fieldLength": 128, "type": 1, "fieldMaxLength": 128, "readOnly": False, "name": "apn_connection_type"},
    {"configId": 0x19, "fieldLength": 128, "type": 1, "fieldMaxLength": 128, "readOnly": False, "name": "server_hostname"},
]

def startDiagnosticSession(stack):
    print("Starting diagnostic session 0xC0")
    stack.send(bytes([0x10, 0xC0]))
    response = stack.recv(block=True, timeout=1.0)
    if response:
        print(f"Response: {response.hex().upper()}")

def readParameter(stack, config_id):
    for attempt in range(0, 5): 
        stack.send(bytes([0x21, config_id]))

        response = stack.recv(block=True, timeout=7.0)
        if response:
            return response

def writeParameter(stack, config_id, value):
    data = bytearray(128 + 3)
    data[0] = 0x3B
    data[1] = config_id
    data[2] = 0x01

    for i, v in enumerate(value):
        data[3 + i] = v
        
    print(f"Write parameter: {data.hex().upper()}")
    
    stack.send(data)
    response = stack.recv(block=True, timeout=2.0)
    if response:
        print(f"Write response: {response.hex().upper()}")

def isotp_error_handler(error):
    logging.warning('IsoTp error happened : %s - %s' % (error.__class__.__name__, str(error)))

def main():
    write_item = None
    write_value = None  
    
    if len(sys.argv) == 2:
        serial_port = sys.argv[1]
    elif len(sys.argv) == 4:
        serial_port = sys.argv[1]
        write_item = sys.argv[2]
        write_value = sys.argv[3] 
    else:
        print("Description: Python script to read/write Nissan Leaf TCU configuration with python-can-isotp")
        print("This script is an example for use with Lawicel CANUSB")
        print()
        print("Read usage: python tcu_config.py <serial_port>")
        print("Read example: python tcu_config.py COM4")
        print()
        print("Write usage: python tcu_config.py <serial_port> <config_item> <value>")
        print("Write example: python tcu_config.py COM4 apn_name hologram")
        print()
        print("All writeable config items:")
        for item in config_items:
            if not item['readOnly']:
                print(item['name'])
        exit()    
    
    # NOTE: If using something else than Lawicel CANUSB, change the slcanBus to your CAN interface
    bus = slcanBus(channel=serial_port, tty_baudrate=921600, bitrate=500000)
        
    addr = isotp.Address(isotp.AddressingMode.Normal_11bits, rxid=0x783, txid=0x746)
    params = {
        'blocking_send' : True,
        # Leaf TCU seems to struggle sending all ISO-TP blocks at once.
        # Blocksize 1 and stmin 100 seem to help with this issue, although sometimes
        # reading still fails - simple retry is needed in that case
        'stmin' : 100,
        'blocksize' : 1
    }

    stack = isotp.CanStack(bus, address=addr, error_handler=isotp_error_handler, params=params)

    try:
        stack.start()
        
        startDiagnosticSession(stack)
        
        # Write specified config item
        if write_item and write_value:
            item = [row for row in config_items if row["name"] == write_item]
            if item and not item[0]['readOnly']:
                writeParameter(stack, item[0]['configId'], bytearray(write_value, "utf-8"))
            else:
                print(f"Config item {write_item} is not writable")
                exit() 
                
        print("Reading all config items:")
        for item in config_items:
            value = readParameter(stack, item['configId'])
            
            if item['type'] == 2  :
                print(f"Name: {item['name']}, Value: {value[2]}, Raw: {value.hex().upper()}")
            elif item['type'] == 3:
                tel_ant_level = int(value[2])
                reception_power = int(value[3])
                error_rate = int(value[4])
                print(f"Name: {item['name']}, Value: ANT:{tel_ant_level},RECEPTION:{reception_power},ERRRATE:{error_rate}")     
            else:
                print(f"Name: {item['name']}, Value: {value[3:].decode('utf-8').strip()}")

    except isotp.BlockingSendFailure:
        print("Isotp send failed")
    finally:
        stack.stop()
        bus.shutdown()

if __name__ == "__main__":
    main()
