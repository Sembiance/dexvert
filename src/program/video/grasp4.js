import {xu} from "xu";
import {Program} from "../../Program.js";

export class grasp4 extends Program
{
	website = "https://winworldpc.com/product/fantavision/1x-dos";
	unsafe  = true;
	loc     = "dos";
	bin     = "GRASP4.EXE";
	args    = r => [r.inFile()];

	// A lot of GL files are just loops, but we can't determine that for sure. Sveral others are actually very long. So 2 minutes is shorter than some durations, but meh.
	dosData   = async r => ({timeout : xu.MINUTE*2, video : await r.outFile("out.mp4", {absolute : true})});
	renameOut = true;
}
