from ipaddress import ip_address

p4 = bfrt.basic.pipe

forwarding = p4.Ingress.forwarding

forwarding.clear()

forwarding.add_with_send_using_port(ingress_port= 132,   port=140)
forwarding.add_with_send_using_port(ingress_port= 140,   port=132)


bfrt.complete_operations()

# Final programming
print("""
******************* PROGAMMING RESULTS *****************
""")
print ("Table forwarding:")
forwarding.dump(table=True)
