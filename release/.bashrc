if [[ $- != *i* ]] ; then
	# Shell is non-interactive.  Be done now!
	return
fi

source /mnt/compendium/sys/.bashrc-common

if [ $(tty) = "/dev/tty1" ]; then
	echo "Preparing RAM disk..."
	ramDiskSize=$(awk '/MemTotal/{print int($2*0.8/1024)}' /proc/meminfo)
	sudo mkdir -p /mnt/ram
	sudo mount -t tmpfs -o size="$ramDiskSize"M,nodev,noatime,mode=0777 tmpfs /mnt/ram
	sudo chmod 777 /mnt/ram
	mkdir -p /mnt/ram/tmp /mnt/ram/portage
	chmod 777 /mnt/ram/tmp
	chmod 775 /mnt/ram/portage
	sudo chown portage:portage /mnt/ram/portage
	
	echo "Preparing scratch disk..."
	sudo parted --script /dev/vdb mklabel msdos
	sudo parted --script /dev/vdb mkpart primary ext4 0% 100%
	sudo mkfs.ext4 -F /dev/vdb1
	sudo mkdir -p /mnt/dexvert
	sudo mount /dev/vdb1 /mnt/dexvert
	sudo chown -R dexvert:dexvert /mnt/dexvert

	echo "Preparing /var/tmp..."
	mkdir -p /mnt/dexvert/var/tmp/portage
	chmod 777 /mnt/dexvert/var/tmp
	sudo chown portage:portage /mnt/dexvert/var/tmp/portage
	sudo chmod 775 /mnt/dexvert/var/tmp/portage
	sudo /etc/init.d/systemd-tmpfiles-setup start

	touch /mnt/ram/tmp/qemuBooted

	echo "Starting dexserver..."
	dexserver
fi
