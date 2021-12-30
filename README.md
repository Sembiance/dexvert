# dexvert - Decompress EXtract conVERT
Convert **962** file formats (out of **1,400** known) into modern browser friendly ones (png/svg/pdf/mp3/mp4/etc.).

Utilizes [Deno](https://deno.land/) to leverage **238** helper programs running on **4** different operating systems under [QEMU](https://www.qemu.org/).

See the lists of [SUPPORTED](SUPPORTED.md) & [UNSUPPORTED](UNSUPPORTED.md) file formats.

## Install and Usage
There is no easy way to install or use this yourself due to 3 factors:
* Many commercial programs and OS's are not included but are needed to convert several formats
* Over **238** programs need to be installed, many with [custom code patches](https://github.com/Sembiance/dexvert-gentoo-overlay)
* Various kernel and OS configurations need to be set just right

Some day I may offer a website where you can upload a file and have it be identified and converted.