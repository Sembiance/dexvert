#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

scratch=400
ram=$(awk '/MemTotal/{print int($2*0.7/1024)}' /proc/meminfo)
tmpDir="/tmp"
cores=$(( $(nproc) * 90 / 100 ))
admin=0

# TODO: Add support for changing IP address assigned to VM
# TODO: Add support for changing cpu it emulates as for some systems 'host' might not work (for example tensor requires avx)

show_usage() {
  echo "Usage: $0 [--scratch=<size>] [--ram=<size>] [--scratchDir=<dir>] [--cores=<num>] [--help]"
  echo "  --scratch=<size>     Set the size of the scratch disk in gigabytes (default: 400GB)."
  echo "  --ram=<size>         Set the size of RAM in megabytes (default: 70% of total system RAM)."
  echo "  --tmpDir=<dir>       Set the tmp directory to use (default: /tmp)."
  echo "  --cores=<num>        Set the number of cores to use (default: 90% of total number of CPUs/cores)."
  echo "  --admin              Run qemu-system-x86_64 interactively in the foreground against the actual HD"
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
      size="${arg#*=}"
      if [[ "$size" =~ ^([0-9]+)$ ]]; then
        ram="$size"
      else
        show_usage
        exit 1
      fi
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

scratchDir="$tmpDir/$(generate_random_string)"
mkdir -p "$scratchDir"

echo "Creating scratch.qcow2 file in $scratchDir with size ${scratch}G..."
scratchFilePath="$scratchDir/scratch.qcow2"
rm -f "$scratchFilePath"
qemu-img create -f qcow2 "$scratchFilePath" "${scratch}G"

hdFilePath="$SCRIPT_DIR/hd.qcow2"

echo "Launching qemu-system-x86_64 with RAM size $ram MB, using $cores cores, and scratch directory $scratchDir..."
if [ "$admin" -eq 1 ]; then
	echo "Launching in ADMIN mode..."
	qemu-system-x86_64 -monitor telnet::47023,server,nowait -machine accel=kvm,dump-guest-core=off -cpu host -vga std -drive format=qcow2,file="$hdFilePath",if=virtio -device virtio-rng-pci -m size="$ram"M -smp "cores=$cores" -boot order=c -netdev user,net=192.168.47.0/24,dhcpstart=192.168.47.47,hostfwd=tcp:127.0.0.1:47022-192.168.47.47:22,id=nd1 -device virtio-net,netdev=nd1 -drive format=qcow2,file="$scratchFilePath",if=virtio -drive format=qcow2,file="$SCRIPT_DIR/admin.qcow2",if=virtio -display curses 
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

	echo "dexserver starting..."
	while ! ssh -i "$SCRIPT_DIR"/dexvert-ssh-key -p 47022 dexvert@127.0.0.1 "[ -e /mnt/ram/dexvert/dexserver.pid ]"; do
		sleep 0.2
	done
	
	echo "dexserver ready!"
	while ps -p "$qemuPID" > /dev/null; do
		sleep 0.2
	done
fi

echo "Cleaning up..."
rm -rf "$scratchDir"
echo "All done!"
