import sys
import time
import argparse
import relay_ft245r

# Set up argument parsing
parser = argparse.ArgumentParser(description="Control a specific relay on an FT245R relay board.")
parser.add_argument('-r', '--relay', type=int, required=True,
                    help='Relay number to control (e.g., 2)')
parser.add_argument('-s', '--state', type=str, required=True,
                    choices=['on', 'off'],
                    help='Relay state to set (on/off)')

args = parser.parse_args()
relay_number = args.relay
relay_state = args.state

rb = relay_ft245r.FT245R()
dev_list = rb.list_dev()

# list of FT245R devices are returned
if len(dev_list) == 0:
    print('No FT245R devices found')
    sys.exit()

# Show their serial numbers
for dev in dev_list:
    print(dev.serial_number)

# Pick the first one for simplicity
dev = dev_list[0]
print('Using device with serial number ' + str(dev.serial_number))

# Connect and set relay state
rb.connect(dev)

if relay_state == 'on':
    rb.switchon(relay_number)
    print(f"Relay {relay_number} switched ON.")
else:
    rb.switchoff(relay_number)
    print(f"Relay {relay_number} switched OFF.")

