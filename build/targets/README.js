import {xu} from "xu";
import {path} from "std";
import {formats} from "../../src/format/formats.js";
import {programs} from "../../src/program/programs.js";
import {QEMUIDS} from "../../src/qemuUtil.js";

const supportedFormats = Object.fromEntries(Object.entries(formats).filter(([, format]) => !format.unsupported));

export default async function buildREADME(xlog)
{
	xlog.info`Writing README.md to disk...`;
	await Deno.writeTextFile(path.join(xu.dirname(import.meta), "..", "..", "README.md"), `# dexvert - Decompress EXtract conVERT
Convert **${Object.keys(supportedFormats).length.toLocaleString()}** file formats (out of **${Object.keys(formats).length.toLocaleString()}** known) into modern equilivants (png/svg/pdf/mp3/mp4/etc.).

Utilizes [Deno](https://deno.land/) to leverage **${Object.keys(programs).length.toLocaleString()}** helper programs running on **${QEMUIDS.length}** different operating systems under [QEMU](https://www.qemu.org/).

See the lists of [SUPPORTED](SUPPORTED.md) & [UNSUPPORTED](UNSUPPORTED.md) file formats.

## Install and Usage
There is no easy way to install or use this yourself due to 3 factors:
* Many commercial programs and OS's are not included but are needed to convert several formats
* Over **${Object.keys(programs).length.toLocaleString()}** programs need to be installed, many with [custom code patches](https://github.com/Sembiance/dexvert-gentoo-overlay)
* Various kernel and OS configurations need to be set just right

Some day I may offer a website where you can upload a file and have it be identified and converted.`);
}
