import {xu} from "xu";
import {path} from "std";
import {fileUtil} from "xutil";
import {formats} from "../../src/format/formats.js";
import {programs} from "../../src/program/programs.js";
import {QEMUIDS} from "../../src/qemuUtil.js";
import {RELEASE} from "../../release/RELEASE.js";

const supportedFormats = Object.fromEntries(Object.entries(formats).filter(([, format]) => !format.unsupported));

export default async function buildREADME(xlog)
{
	xlog.info`Writing README.md to disk...`;
	await fileUtil.writeTextFile(path.join(xu.dirname(import.meta), "..", "..", "README.md"), `# dexvert - **D**ecompress **EX**tract con**VERT**
Convert **${Object.keys(supportedFormats).length.toLocaleString()}** file formats (out of **${Object.keys(formats).length.toLocaleString()}** known) into modern equilivants (png/svg/pdf/mp3/mp4/etc.)

See the lists of [SUPPORTED](SUPPORTED.md) & [UNSUPPORTED](UNSUPPORTED.md) file formats

Utilizes [Deno](https://deno.land/) and **${Object.keys(programs).length.toLocaleString()}** helper programs running on **${QEMUIDS.length}** different operating systems under [QEMU](https://www.qemu.org/)

**THIS PROJECT IS NOT MAINTAINED**<br>
**IT WILL NOT BE UPDATED**<br>
**BUGS WILL NOT BE FIXED**<br>
**PULL REQUESTS WILL BE IGNORED**<br>

${RELEASE.README_TEXT}`);
}
