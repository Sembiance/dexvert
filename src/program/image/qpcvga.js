import {xu} from "xu";
import {Program} from "../../Program.js";

export class qpcvga extends Program
{
	unsafe    = true;
	loc       = "dos";
	bin       = "QPCVGA.EXE";
	args      = r => [r.inFile(), "/K"];
	dosData   = async r => ({timeout : xu.SECOND*20, keys : ["q", {delay : xu.SECOND*5}, "c"], screenshot : {filePath : await r.outFile("out.png", {absolute : true}), frameLoc : 90}});
	renameOut = true;
}
