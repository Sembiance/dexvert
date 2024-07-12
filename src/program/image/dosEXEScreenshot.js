import {xu} from "xu";
import {path} from "std";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";

export class dosEXEScreenshot extends Program
{
	website   = "https://github.com/Sembiance/dexvert/";
	unsafe    = true;
	loc       = "dos";
	flags   = {
		timeout  : "Timeout after X ms. Default: 1 minute",
		frameLoc : "Frame location (percentage of max) to take screenshot at. Default: 30"
	};
	pre       = async r => await fileUtil.writeTextFile(path.join(r.cwd, "DOSEXE.bat"), ["@ECHO OFF", r.inFile(), "SLEEP 2"].join("\n"));
	bin       = "DOSEXE.bat";
	dosData   = async r => ({runIn : "absolute", timeout : r.flags.timeout || xu.MINUTE, screenshot : {filePath : await r.outFile("out.png", {absolute : true}), frameLoc : r.flags.frameLoc || 30}});
	renameOut = true;
}
