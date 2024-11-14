import {xu} from "xu";
import {path} from "std";
import {Program} from "../../Program.js";
import {fileUtil} from "xutil";

export class dosEXEExtract extends Program
{
	website   = "https://github.com/Sembiance/dexvert/";
	unsafe    = true;
	loc       = "dos";
	flags   = {
		exeArgs : "Extra args to pass to the EXE (this is expressed just as a string and is saved into a BAT file)",
		timeout : "Timeout after X ms. Default: 1 minute"
	};
	pre       = async r => await fileUtil.writeTextFile(path.join(r.cwd, "DOSEXE.bat"), ["@ECHO OFF", `CD ${path.basename(r.outDir()).toUpperCase()}`, `..\\${r.inFile().toUpperCase()}${r.flags.exeArgs ? ` ${r.flags.exeArgs}` : ""}`, "EXIT"].join("\n"));
	bin       = "DOSEXE.bat";
	dosData   = r => ({runIn : "absolute", keys : [{delay : xu.SECOND*2}, "y"], timeout : r.flags.timeout || xu.MINUTE});
	renameOut = true;
}
