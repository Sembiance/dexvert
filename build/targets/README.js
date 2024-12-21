import {xu} from "xu";
import {path} from "std";
import {fileUtil} from "xutil";
import {formats, init as initFormats} from "../../src/format/formats.js";
import {programs, init as initPrograms} from "../../src/program/programs.js";

export default async function README(xlog)
{
	await initPrograms(xlog);
	await initFormats(xlog);

	const supportedFormats = Object.fromEntries(Object.entries(formats).filter(([, format]) => !format.unsupported));

	xlog.info`Writing README.md to disk...`;
	await fileUtil.writeTextFile(path.join(import.meta.dirname, "..", "..", "README.md"), `# dexvert - **D**ecompress **EX**tract con**VERT**
Convert **${Object.keys(supportedFormats).length.toLocaleString()}** file formats (out of **${Object.keys(formats).length.toLocaleString()}** known) into modern equilivants (png/svg/pdf/mp3/mp4/etc.)

See the lists of [SUPPORTED](SUPPORTED.md) & [UNSUPPORTED](UNSUPPORTED.md) file formats

Utilizes **${Object.keys(programs).length.toLocaleString()}** helper programs running on **4** different operating systems under various emulators.

[discmaster.textfiles.com](http://discmaster.textfiles.com/) utilizes this to convert and extract old files. If you find a file that does not convert properly, submit an issue.

This project is not currently ready for public use.
`);
}
