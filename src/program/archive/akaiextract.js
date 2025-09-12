import {xu} from "xu";
import {Program} from "../../Program.js";

export class akaiextract extends Program
{
	website    = "https://www.linuxsampler.org/libgig/";
	package    = "media-libs/libgig";
	bin        = "akaiextract";
	args       = r => [r.inFile(), r.outDir()];
	runOptions = () => ({stdinData : `y`});
	renameOut  = false;
}
