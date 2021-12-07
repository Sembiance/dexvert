import {xu} from "xu";
import {Program} from "../../Program.js";

export class sndh2raw extends Program
{
	website = "https://github.com/Sembiance/sndh2raw";
	package = "media-sound/sndh2raw";
	unsafe  = true;
	bin     = "sndh2raw";
	args    = r => [r.inFile(), r.outDir()];
	chain   = r =>
	{
		Object.assign(r.meta, xu.parseJSON(r.stdout));
		return `sox[type:raw][rate:${r.meta.samplingRate}][encoding:signed-integer][endianness:little][bits:16][channels:2]`;
	};
}
