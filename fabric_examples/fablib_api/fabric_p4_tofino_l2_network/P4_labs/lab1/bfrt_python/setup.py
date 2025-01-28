import sys
import io
import contextlib
import re

# Get the P4 pipeline object
p4 = bfrt.basic.pipe

# Capture `bfrt.port.dump(from_hw=True)` output
with io.StringIO() as buf, contextlib.redirect_stdout(buf):
    #bfrt.port.port.dump(json=True, table=True, return_ents=True, from_hw=True)
    bfrt.port.port.dump(from_hw=True)
    port_dump_output = buf.getvalue()

# Dictionary to store port mapping
port_mapping = {}

# Regex patterns for extracting port name and device port
dev_port_pattern = re.compile(r"\$DEV_PORT\s+:\s+(0x[0-9A-Fa-f]+)")
port_name_pattern = re.compile(r"\$PORT_NAME\s+:\s+(\S+)")

# Parsing the output
current_dev_port = None
for line in port_dump_output.split("\n"):
    dev_port_match = dev_port_pattern.search(line)
    if dev_port_match:
        current_dev_port = int(dev_port_match.group(1), 16)  # Convert hex to decimal

    port_name_match = port_name_pattern.search(line)
    if port_name_match and current_dev_port is not None:
        port_name = port_name_match.group(1)
        port_mapping[port_name] = current_dev_port
        current_dev_port = None  # Reset for the next entry

print(f"Port Mapping: {port_mapping}")

def main(ingress_logical, egress_logical):
    """Configures forwarding using logical-to-device port mappings."""

    # Convert logical ports to device ports
    ingress_port = port_mapping.get(f"{ingress_logical}/0")
    egress_port = port_mapping.get(f"{egress_logical}/0")

    if ingress_port is None or egress_port is None:
        print(f"Error: One or both logical ports ({ingress_logical}, {egress_logical}) not found!")
        return

    # Get forwarding table
    forwarding = p4.Ingress.forwarding

    # Clear and program forwarding table
    forwarding.clear()
    forwarding.add_with_send_using_port(ingress_port=ingress_port, port=egress_port)
    forwarding.add_with_send_using_port(ingress_port=egress_port, port=ingress_port)

    bfrt.complete_operations()

    # Print the programmed forwarding table
    print("\n******************* PROGRAMMING RESULTS *****************")
    print("Table forwarding:")
    forwarding.dump(table=True)

if __name__ == "__main__":
    ingress_logical = 1
    egress_logical = 2

    main(ingress_logical, egress_logical)