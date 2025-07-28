#!/bin/bash

set -e

# Detect IP type
if ping6 -c 1 google.com &> /dev/null; then
    man_ip_type=ipv6
else
    man_ip_type=ipv4
fi

# Detect OS and version
source /etc/os-release
os_id=$ID
os_version_id=$(echo $VERSION_ID | cut -d'.' -f1)

echo "Detected OS: $os_id, Version: $os_version_id"

install_ubuntu_common() {
    sudo apt-get update -y
    sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common gnupg lsb-release
    curl -fsSL https://get.docker.com | sudo sh
    sudo mkdir -p /etc/docker
    sudo usermod -aG docker ubuntu
    sudo apt-get install -y openvswitch-switch
    sudo systemctl enable --now openvswitch-switch
    sudo apt-get install -y build-essential wget tcpdump iftop python3-pip
    sudo apt install -y python3-dev build-essential libatlas-base-dev
}

install_python_libs() {
    python3 -m pip install docker rpyc --user --break-system-packages || python3 -m pip install docker rpyc --user
}

ensure_pip39() {
    if ! command -v pip3.9 &>/dev/null; then
        echo "pip3.9 not found, installing..."
        curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.9
        if ! echo "$PATH" | grep -q "/usr/local/bin"; then
            echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
            export PATH="/usr/local/bin:$PATH"
            echo "Added /usr/local/bin to PATH. Please restart your terminal or run 'source ~/.bashrc'"
        fi
    fi
}

install_rocky_common() {
    sudo dnf install -y epel-release
    sudo dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
    sudo dnf install -y docker-ce docker-ce-cli containerd.io
    sudo mkdir -p /etc/docker
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker rocky
    sudo dnf install -y firewalld git
    sudo dnf install -y python3-devel gcc gcc-c++ redhat-rpm-config
    sudo dnf install expect -y
    sudo systemctl enable --now firewalld
    sudo firewall-cmd --zone=public --add-port=5201/tcp --permanent
    sudo firewall-cmd --zone=public --add-port=5201/udp --permanent
    sudo firewall-cmd --reload
}

host_tune() {
    echo "Applying host tuning settings..."
    cat >> /etc/sysctl.conf <<EOL
# allow testing with buffers up to 128MB
net.core.rmem_max = 536870912
net.core.wmem_max = 536870912
# increase Linux autotuning TCP buffer limit to 64MB
net.ipv4.tcp_rmem = 4096 87380 536870912
net.ipv4.tcp_wmem = 4096 65536 536870912
# recommended default congestion control is htcp or bbr
net.ipv4.tcp_congestion_control = bbr
# recommended for hosts with jumbo frames enabled
net.ipv4.tcp_mtu_probing = 1
# recommended to enable 'fair queueing'
net.core.default_qdisc = fq
EOL
    sysctl --system

    for dev in $(basename -a /sys/class/net/*); do
        ip link set dev $dev mtu 9000 || true
    done
}

# Main execution logic
case "$os_id" in
    ubuntu)
        case "$os_version_id" in
            20)
                install_ubuntu_common
                sudo apt-get install -y \
                    zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev \
                    python3.9 python3.9-full
                python3.9 -m pip install docker rpyc --user
                ;;
            22|24)
                install_ubuntu_common
                sudo apt-get install -y \
                    checkinstall libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
                install_python_libs
                ;;
            *)
                echo "Unsupported Ubuntu version: $os_version_id"
                exit 1
                ;;
        esac
        ;;
    rocky)
        case "$os_version_id" in
            8)
                install_rocky_common
                sudo dnf install -y https://repos.fedorapeople.org/repos/openstack/openstack-yoga/rdo-release-yoga-1.el8.noarch.rpm
                sudo dnf install -y openvswitch libibverbs tcpdump net-tools python3.9 vim iftop
                ensure_pip39
                pip3.9 install docker rpyc --user
                sudo systemctl enable --now openvswitch
                sudo sysctl --system
                ;;
            9)
                install_rocky_common
                sudo dnf install -y centos-release-nfv-openvswitch
                sudo dnf install -y openvswitch3.3 libibverbs tcpdump net-tools python vim iftop
                ensure_pip39
                pip3.9 install docker rpyc --user
                sudo systemctl enable --now openvswitch
                sudo sysctl --system
                ;;
            *)
                echo "Unsupported Rocky version: $os_version_id"
                exit 1
                ;;
        esac
        ;;
    *)
        echo "Unsupported OS: $os_id"
        exit 1
        ;;
esac

host_tune
