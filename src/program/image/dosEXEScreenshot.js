import {xu} from "xu";
import {path} from "std";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";

export class dosEXEScreenshot extends Program
{
	website   = "https://github.com/Sembiance/dexvert/";
	unsafe    = true;
	loc       = "dos";
	pre       = async r => await fileUtil.writeTextFile(path.join(r.cwd, "DOSEXE.bat"), ["@ECHO OFF", r.inFile(), "SLEEP 2"].join("\n"));
	bin       = "DOSEXE.bat";
	dosData   = async r => ({runIn : "absolute", screenshot : {filePath : await r.outFile("out.png", {absolute : true}), frameLoc : 30}});
	renameOut = true;
}
