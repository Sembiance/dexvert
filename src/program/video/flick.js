import {xu} from "xu";
import {Program} from "../../Program.js";

export class flick extends Program
{
	website   = "http://cd.textfiles.com/silvercollection/disc2/GRAPHVEW/DASFLICK.ARJ";
	unsafe    = true;
	notes     = "FLICK.EXE loops the video forever, haven't figured out a way to stop after once. So I just record for 40 seconds.";
	loc       = "dos";
	bin       = "FLICK.EXE";
	args      = r => ["-qa", r.inFile({backslash : true})];
	dosData   = async r => ({timeout : xu.SECOND*40, video : await r.outFile("out.mp4", {absolute : true})});
	renameOut = true;
}
