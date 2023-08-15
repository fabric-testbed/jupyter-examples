echo "table_add MyIngress.forwarding MyIngress.forward 0 => 1" | simple_switch_CLI
echo "table_add MyIngress.forwarding MyIngress.forward 1 => 0" | simple_switch_CLI
