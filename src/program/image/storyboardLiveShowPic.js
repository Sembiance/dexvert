import {xu} from "xu";
import {Program} from "../../Program.js";

export class storyboardLiveShowPic extends Program
{
	website   = "https://winworldpc.com/product/ibm-storyboard/live-20";
	unsafe    = true;
	loc       = "dos";
	bin       = "SBLIVE/SHOWPIC.EXE";
	args      = r => [r.inFile()];
	dosData   = async r => ({keys : [{delay : xu.SECOND*15}, "Escape"], screenshot : {filePath : await r.outFile("out.png", {absolute : true}), frameLoc : 100}});
	renameOut = true;
}

