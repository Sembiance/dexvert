import {Program} from "../../Program.js";

export class xbtfextractor extends Program
{
	website   = "https://github.com/larshall/xbtfextractor";
	package   = "media-gfx/xbtfextractor";
	bin       = "xbtfextractor";
	args      = r => ["-o", r.outDir(), r.inFile()];
	renameOut = false;
}
