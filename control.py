import sys
import time
import argparse
import relay_ft245r

# Set up argument parsing
parser = argparse.ArgumentParser(description="Control a specific relay on an FT245R relay board.")
parser.add_argument('-r', '--relay', type=int, required=True,
                    help='Relay number to control or check (e.g., 2)')

# Create a mutually exclusive group for state and checkifon
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-s', '--state', type=str, choices=['on', 'off'],
                   help='Relay state to set (on/off)')
group.add_argument('--checkifon', action='store_true',
                   help='Check if the given relay is ON. Exit with code 0 if ON, 1 if OFF.')

args = parser.parse_args()
relay_number = args.relay

rb = relay_ft245r.FT245R()
dev_list = rb.list_dev()

# list of FT245R devices are returned
if len(dev_list) == 0:
    print('No FT245R devices found')
    sys.exit(2)  # Exit code 2 to indicate no device found

# Show their serial numbers
for dev in dev_list:
    print(dev.serial_number)

# Pick the first one for simplicity
dev = dev_list[0]
print('Using device with serial number ' + str(dev.serial_number))

# Connect to device
rb.connect(dev)

if args.checkifon:
    # Check if relay is on
    status = rb.getstatus(relay_number)
    # getstatus returns 1 if ON, 0 if OFF
    # We want to exit with code 0 if ON, 1 if OFF
    if status == 1:
        sys.exit(0)  # ON → exit code 0
    else:
        sys.exit(1)  # OFF → exit code 1
else:
    # We have a state to set (on/off)
    relay_state = args.state

    # Double commands due to device quirk
    if relay_state == 'on':
        rb.switchon(relay_number)
        rb.switchon(relay_number)
        print(f"Relay {relay_number} switched ON.")
    else:
        rb.switchoff(relay_number)
        rb.switchoff(relay_number)
        print(f"Relay {relay_number} switched OFF.")

    # Normal successful completion
    sys.exit(0)

