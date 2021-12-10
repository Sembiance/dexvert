import {Program} from "../../Program.js";

export class swfextract extends Program
{
	website   = "http://www.swftools.org/";
	package   = "media-gfx/swftools";
	bin       = "swfextract";
	args      = r => ["--outputformat", `${r.outDir()}/%06d.%s`, "-a", "1-", r.inFile()];
	verify    = (r, dexFile) => dexFile.size>1;
	renameOut = false;
}
