import {Program} from "../../Program.js";

export class threeDM2GLB extends Program
{
	website   = "https://github.com/Sembiance/dexvert";
	package   = "media-gfx/3dm2glb";
	bin       = "3dm2glb";
	args      = async r => [r.inFile(), await r.outFile("out.glb")];
	renameOut = true;
}
