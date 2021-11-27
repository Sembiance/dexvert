# dexvert - Decompress EXtract conVERT
Convert **337** file formats (out of **613** known) into modern browser friendly equilivants (png, svg, pdf, mp3, mp4, etc.).

Utilizes [Deno](https://deno.land/) to leverage **59** helper programs running on **4** different operating systems under [QEMU](https://www.qemu.org/).

See [SUPPORTED.md](SUPPORTED.md) file formats and [UNSUPPORTED.md](UNSUPPORTED.md) file formats.

Multiple file samples are available for each supported format: https://telparia.com/fileFormatSamples/

## Install and Usage
There is no easy way to install or use this yourself due to 3 factors:
* Multiple commercial programs and operating systems are required to convert certain formats
* Over **59** programs need to be installed, several with [custom code patches](https://github.com/Sembiance/dexvert-gentoo-overlay)
* Various kernel and OS configurations need to be set just right

Some day I plan on making a website available where you can upload a file and have it be identified and converted.