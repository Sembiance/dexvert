cfdecrypt
=========

developed by Matt Chapman www.zmatt.net, see cfdecrypt.c
----------------------------------------------------------------------

Windows
-------
See /Windows

Linux
-----
###Try the binaries included or compile it yourself, download a copy of openssl source code and extract it in your home directory:

###Prepare
mkdir ~/cfdecrypt

####Download cfdecrypt files here
cd ~
wget http://www.openssl.org/source/openssl-1.0.0d.tar.gz ~
tar -xvf openssl-1.0.0d.tar.gz

###Copy the source to this folder:
cp cfdecrypt.c ~/openssl-1.0.0d/crypto/des

###Switch to that folder
cd ~/openssl-1.0.0d/crypto/des

###Compile
gcc -static ~/openssl-1.0.0d/crypto/des/des_old.c -lcrypto ~/openssl-1.0.0d/crypto/des/cfdecrypt.c -o cfdecrypt
gcc  ~/openssl-1.0.0d/crypto/des/cfiscrypted.c -o cfiscrypted

###Copy the executables to somewhere convenient
cp ./cfdecrypt ~/cfdecrypt
cp ./cfiscrypted ~/cfdecrypt

###Check out the bash script provided
~/cfdecrypt/cfdecrypt.sh --help
