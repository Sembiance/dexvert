
import {Program} from "../../Program.js";

export class drawview extends Program
{
	website       = "http://www.keelhaul.me.uk/acorn/drawview/";
	gentooPackage = "media-gfx/drawview";
	gentooOverlay = "dexvert";
	bin           = "drawview";
	runOptions    = ({virtualX : true});
	args          = r => ["-e", r.outDir(), r.inFile()]
	chain         = "deDynamicSVG[autoCrop]"	// The SVGs from acorn are often horribly cropped wrong and cut off, autoCrop flag will fix that will fix that
}
