distro=$(. /etc/os-release; echo ${ID}${VERSION_ID//./})

architecture='x86_64'

sudo DEBIAN_FRONTEND=noninteractive  apt-get install -y pciutils && lspci | grep 'NVIDIA|3D controller'
sudo DEBIAN_FRONTEND=noninteractive  apt-get -q update
sudo DEBIAN_FRONTEND=noninteractive  apt-get -q install -y linux-headers-$(uname -r) gcc

wget https://developer.download.nvidia.com/compute/cuda/repos/$distro/$architecture/cuda-keyring_1.1-1_all.deb
sudo DEBIAN_FRONTEND=noninteractive dpkg -i cuda-keyring_1.1-1_all.deb
sudo DEBIAN_FRONTEND=noninteractive  apt-get -q update
sudo DEBIAN_FRONTEND=noninteractive  apt-get -q install -y cuda

distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
    && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
    && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo DEBIAN_FRONTEND=noninteractive  apt -q update 
sudo DEBIAN_FRONTEND=noninteractive sudo apt install -q -y nvidia-container-toolkit
sudo DEBIAN_FRONTEND=noninteractive systemctl restart docker
