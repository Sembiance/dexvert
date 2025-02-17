import {xu} from "xu";
import {Program} from "../../Program.js";

export class laughingDog extends Program
{
	website   = "http://cd.textfiles.com/ftp.wwiv.com/pub/ANSI/HDISP13A.ZIP";
	unsafe    = true;
	loc       = "dos";
	bin       = "LAUGHDOG/HD.EXE";
	args      = r => [r.inFile(), "/c"];
	dosData   = async r => ({keys : [{delay : xu.SECOND*5}, "Escape"], screenshot : {filePath : await r.outFile("out.png", {absolute : true}), frameLoc : 90}});
	renameOut = true;
}

