

/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/
typedef bit<9>  egressSpec_t;

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }
    
    action forward(egressSpec_t port) {
        standard_metadata.egress_spec = port;
    }
    
    table forwarding {
        key = {
            standard_metadata.ingress_port:exact;
        }
        actions = {
            forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }
    
    apply {
        forwarding.apply();
    }
}