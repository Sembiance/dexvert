import {xu} from "xu";
import {path} from "std";
import {fileUtil} from "xutil";
import {formats, init as initFormats} from "../../src/format/formats.js";
import {programs, init as initPrograms} from "../../src/program/programs.js";
//import {RELEASE} from "../../release/RELEASE.js";	// TODO update RELEASE.js with the new release info
// TODO add this file back to build.js

export default async function buildREADME(xlog)
{
	await initPrograms(xlog);
	await initFormats(xlog);

	const supportedFormats = Object.fromEntries(Object.entries(formats).filter(([, format]) => !format.unsupported));

	xlog.info`Writing README.md to disk...`;
	await fileUtil.writeTextFile(path.join(xu.dirname(import.meta), "..", "..", "README.md"), `# dexvert - **D**ecompress **EX**tract con**VERT**
Convert **${Object.keys(supportedFormats).length.toLocaleString()}** file formats (out of **${Object.keys(formats).length.toLocaleString()}** known) into modern equilivants (png/svg/pdf/mp3/mp4/etc.)

See the lists of [SUPPORTED](SUPPORTED.md) & [UNSUPPORTED](UNSUPPORTED.md) file formats

Utilizes [Deno](https://deno.land/) and **${Object.keys(programs).length.toLocaleString()}** helper programs running on **4** different operating systems under various emulators.

This project is not currently ready for public use. Efforts are underway to make it usable by others.
`);	// TODO Add back in ${RELEASE.README_TEXT}
}
