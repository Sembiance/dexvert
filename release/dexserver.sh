#!/bin/bash

# So this script essentially is in charge of starting up a QEMU instance that all dexvert operations take place within

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

scratch=100
ram=$(awk '/MemTotal/{print int($2*0.7/1024)}' /proc/meminfo)
tmpDir="/tmp"
cores=$(( $(nproc) * 95 / 100 ))
admin=0

# TODO: Add support for changing IP address assigned to VM
# TODO: Add support for a publicHost and publicPort option that will tunnel from public to the VM's ip for remote ssh access

show_usage() {
  echo "Usage: $0 [--scratch=<size>] [--ram=<size>] [--scratchDir=<dir>] [--cores=<num>] [--help]"
  echo "  --scratch=<size>     Set the size of the scratch disk in gigabytes (default: 100GB). This is where output files are placed while being processed."
  echo "  --ram=<size>         Set the size of RAM in megabytes (eg 100 for 100MB) or 0.7 for 70% of RAM (default 0.8 or 80% of total system RAM)."
  echo "  --tmpDir=<dir>       Set the tmp directory to use (default: /tmp)."
  echo "  --cores=<num>        Set the number of cores to use. Either # like 30 for 30 cores or 0.7 for 70% of cores (default 0.95 or 95%)."
  echo "  --help               Display this help message."
}

function generate_random_string() {
	tr -dc 'a-zA-Z0-9' < /dev/urandom | fold -w 10 | head -n 1
}

for arg in "$@"; do
  case $arg in
    --scratch=*)
      size="${arg#*=}"
      if [[ "$size" =~ ^([0-9]+)$ ]]; then
        scratch="$size"
      else
        show_usage
        exit 1
      fi
      shift
      ;;
    --ram=*)
	  ram="${arg#*=}"
      shift
      ;;
    --tmpDir=*)
      tmpDir="${arg#*=}"
      shift
      ;;
    --cores=*)
      cores="${arg#*=}"
      shift
      ;;
    --admin)
      admin=1
      shift
      ;;
    --help)
      show_usage
      exit 0
      ;;
    *)
      show_usage
      exit 1
      ;;
  esac
done

if [[ "$cores" =~ ^[0-9]+\.[0-9]+$ ]]; then
    cores=$(echo "$(nproc) * $cores" | bc)
	cores=$(printf "%.0f" "$cores")
fi

if [[ "$ram" =~ ^[0-9]+\.[0-9]+$ ]]; then
	ram=$(awk '/MemTotal/{print int($2 * '$ram' / 1024)}' /proc/meminfo)
fi

scratchDir="$tmpDir/$(generate_random_string)"
mkdir -p "$scratchDir"

scratchAvailable=$(command df -BG --output=avail "$tmpDir" | tail -n1 | tr -d 'G ')
if [ "$scratchAvailable" -lt "$scratch" ]; then
	echo "Not enough space in $tmpDir to create scratch disk. Only $scratchAvailable GB available, but --scratch is set to $scratch GB."
	exit
fi

echo "Creating scratch.qcow2 file in $scratchDir with size ${scratch}G..."
scratchFilePath="$scratchDir/scratch.qcow2"
rm -f "$scratchFilePath"
qemu-img create -f qcow2 "$scratchFilePath" "${scratch}G"

hdFilePath="$SCRIPT_DIR/hd.qcow2"

echo "Launching qemu-system-x86_64 with RAM size $ram MB, using $cores cores, and scratch directory $scratchDir..."
if [ "$admin" -eq 1 ]; then
	echo "Launching in ADMIN mode..."
	qemu-system-x86_64 -monitor telnet::47023,server,nowait -machine accel=kvm,dump-guest-core=off -cpu qemu64,+avx,+avx2,+aes,+mmx,+mmxext,+popcnt,+sse,+sse2,+sse4.1,+sse4.2,+ssse3 -vga std -drive format=qcow2,file="$hdFilePath",if=virtio -device virtio-rng-pci -m size="$ram"M -smp "cores=$cores" -boot order=c -netdev user,net=192.168.47.0/24,dhcpstart=192.168.47.47,hostfwd=tcp:127.0.0.1:47022-192.168.47.47:22,id=nd1 -device virtio-net,netdev=nd1 -drive format=qcow2,file="$scratchFilePath",if=virtio -drive format=qcow2,file="$SCRIPT_DIR/admin.qcow2",if=virtio -display curses
else
	echo "Creating backing file of hd.qcow2..."
	hdBackingFilePath="$scratchDir/hd_backing.qcow2"
	rm -f "$hdBackingFilePath"
	qemu-img create -f qcow2 -b "$hdFilePath" -F qcow2 "$hdBackingFilePath"

	pidFilePath="$scratchDir/qemu.pid"
	rm -f "$pidFilePath"
	qemu-system-x86_64 -monitor telnet::47023,server,nowait -machine accel=kvm,dump-guest-core=off -cpu host -vga std -drive format=qcow2,file="$hdBackingFilePath",if=virtio -device virtio-rng-pci -m size="$ram"M -smp "cores=$cores" -boot order=c -netdev user,net=192.168.47.0/24,dhcpstart=192.168.47.47,hostfwd=tcp:127.0.0.1:47022-192.168.47.47:22,id=nd1 -device virtio-net,netdev=nd1 -drive format=qcow2,file="$scratchFilePath",if=virtio -daemonize -pidfile "$pidFilePath" -display none

	echo "QEMU starting..."
	while [ ! -f "$pidFilePath" ]; do
		sleep 0.2
	done

	qemuPID="$(cat "$pidFilePath")"

	function clean_up
	{
		echo "Signal caught. Stopping dexserver..."
		kill "$qemuPID"
	}

	trap clean_up SIGINT

	echo "QEMU booting..."
	while ! ssh -i "$SCRIPT_DIR"/dexvert-ssh-key -p 47022 dexvert@127.0.0.1 "[ -e /mnt/ram/tmp/qemuBooted ]"; do
		sleep 0.2
	done

	echo "dexserver starting (can take up to 10 minutes)..."
	while ! ssh -i "$SCRIPT_DIR"/dexvert-ssh-key -p 47022 dexvert@127.0.0.1 "[ -e /mnt/ram/dexvert/dexserver.pid ]"; do
		sleep 0.2
	done
	
	echo "dexserver ready!!!"
	while ps -p "$qemuPID" > /dev/null; do
		sleep 0.2
	done
fi

echo "Cleaning up..."
rm -rf "$scratchDir"
echo "All done!"
