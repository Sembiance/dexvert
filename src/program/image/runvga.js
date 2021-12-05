import {xu} from "xu";
import {Program} from "../../Program.js";

export class runvga extends Program
{
	website = "https://en.wikipedia.org/wiki/3D_Construction_Kit";
	unsafe  = true;
	loc     = "dos";
	bin     = "RUNVGA.EXE";
	args    = r => [r.inFile()];
	dosData = async r => ({timeout : xu.SECOND*20, keys : ["1", {delay : xu.SECOND*5}, "c"], screenshot : {filePath : await r.outFile("out.png", {absolute : true}), frameLoc : 90}});
}
