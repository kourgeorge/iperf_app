# Variables
IPERF_VERSION = 3.12
IPERF_URL = https://iperf.fr/download/source/iperf-$(IPERF_VERSION).tar.gz
INSTALL_DIR = /usr/local/bin

# Default target
all: install_iperf

# Download iPerf source
download_iperf:
	wget $(IPERF_URL) -O iperf-$(IPERF_VERSION).tar.gz

# Extract the downloaded tarball
extract_iperf: download_iperf
	tar -xzf iperf-$(IPERF_VERSION).tar.gz

# Build and install iPerf
install_iperf: extract_iperf
	cd iperf-$(IPERF_VERSION) && ./configure && make && sudo make install

# Clean up the downloaded files and build artifacts
clean:
	rm -rf iperf-$(IPERF_VERSION) iperf-$(IPERF_VERSION).tar.gz