import {xu} from "xu";
import {fileUtil} from "xutil";
import {path} from "std";
import {formats} from "../../src/format/formats.js";
import {programs} from "../../src/program/programs.js";
import {QEMUIDS} from "../../src/qemuUtil.js";

const supportedFormats = Object.fromEntries(Object.entries(formats).filter(([, format]) => !format.unsupported));

export default async function buildREADME()
{
	xu.log3`Writing README.md to disk...`;
	await fileUtil.writeFile(path.join(xu.dirname(import.meta), "..", "..", "README.md"), `# dexvert - Decompress EXtract conVERT
Convert **${Object.keys(supportedFormats).length.toLocaleString()}** file formats (out of **${Object.keys(formats).length.toLocaleString()}** known) into modern browser friendly equilivants (png, svg, pdf, mp3, mp4, etc.).

Utilizes [Deno](https://deno.land/) to leverage **${Object.keys(programs).length.toLocaleString()}** helper programs running on **${QEMUIDS.length}** different operating systems under [QEMU](https://www.qemu.org/).

See [SUPPORTED.md](SUPPORTED.md) file formats and [UNSUPPORTED.md](UNSUPPORTED.md) file formats.

Multiple file samples are available for each supported format: https://telparia.com/fileFormatSamples/

## Install and Usage
There is no easy way to install or use this yourself due to 3 factors:
* Multiple commercial programs and operating systems are required to convert certain formats
* Over **${Object.keys(programs).length.toLocaleString()}** programs need to be installed, several with [custom code patches](https://github.com/Sembiance/dexvert-gentoo-overlay)
* Various kernel and OS configurations need to be set just right

Some day I plan on making a website available where you can upload a file and have it be identified and converted.`);
}
