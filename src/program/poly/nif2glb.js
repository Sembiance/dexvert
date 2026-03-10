import {Program} from "../../Program.js";

export class nif2glb extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	package   = "media-gfx/nif2glb";
	bin       = "nif2glb";
	args      = async r => [r.inFile(), await r.outFile("out.glb")];
	renameOut = true;
}
