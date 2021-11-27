# dexvert - Decompress EXtract conVERT
Convert **337** file formats (out of **613** known) into modern browser friendly ones (png/svg/pdf/mp3/mp4/...).

Utilizes [Deno](https://deno.land/) to leverage **59** helper programs running on **4** different operating systems under [QEMU](https://www.qemu.org/).

See lists of [SUPPORTED](SUPPORTED.md) and [UNSUPPORTED](UNSUPPORTED.md) file formats.

## Install and Usage
There is no easy way to install or use this yourself due to 3 factors:
* Many commercial programs and OS's are not included but are needed to convert several formats
* Over **59** programs need to be installed, many with [custom code patches](https://github.com/Sembiance/dexvert-gentoo-overlay)
* Various kernel and OS configurations need to be set just right

Some day I may offer a website where you can upload a file and have it be identified and converted.