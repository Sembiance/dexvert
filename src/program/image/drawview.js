
import {Program} from "../../Program.js";

export class drawview extends Program
{
	website    = "http://www.keelhaul.me.uk/acorn/drawview/";
	package    = "media-gfx/drawview";
	bin        = "drawview";
	runOptions = ({virtualX : true});
	args       = r => ["--export", r.outDir(), "--format", "SVG", "--overwrite", r.inFile()];
	renameOut  = true;
	chain      = "deDynamicSVG[autoCrop]";	// The SVGs from acorn are often horribly cropped wrong and cut off, autoCrop flag will fix that will fix that
}
