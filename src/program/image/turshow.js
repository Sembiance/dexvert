import {Program} from "../../Program.js";

export class turshow extends Program
{
	website = "http://fileformats.archiveteam.org/wiki/NAPLPS";
	unsafe  = true;
	loc     = "dos";
	bin     = "TURSHOW/TURSHOW.EXE";
	args    = r => [r.inFile()];
	dosData = async r => ({screenshot : {filePath : await r.outFile("out.png", {absolute : true}), frameLoc : 95}});
}
