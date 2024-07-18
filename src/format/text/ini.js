import {Format} from "../../Format.js";

export class ini extends Format
{
	name           = "INI File";
	website        = "http://fileformats.archiveteam.org/wiki/INI";
	ext            = [".ini", ".inf", ".cfg", ".conf", ".nfo"];
	forbidExtMatch = [".cfg", ".conf", ".nfo"];
	magic          = [
		// general INI types
		"Generic INI configuration", "Windows desktop.ini", "INF Datei", "Windows Initialization settings",

		// specific INI Types: We keep these identified as 'ini' due to the untouch and 'metaProvider' check. I could in the future create a new format for each of these, but I'd have to include thoses checks below (maybe after I update formats.js to better handle this)
		"InstallShield Setup config", "Windows Dial-Up Networking configuration", "Microsoft Setup Toolkit for Windows files List", "LapLink 5 settings", "InstallShield Language Identifier", "TagInfo data", "TagInfo, ASCII text", "Delphi project Options",
		"BRIEF session info", "Windows Explorer Command Shell File", "Windows Explorer Shell Command File", "AOL Modem parameters", "McAfee VirusScan for Windows settings", "Microsoft C/C++ project Status info", "Blob Sculptor for Windows model", "TagInfo",
		"WinAmp/SHOUTcast PlayList", /^PLS playlist/, /^Windows [Cc]odepage translator/
	];
	priority       = this.PRIORITY.LOW;
	untouched      = dexState => dexState.meta.valid && (dexState.meta.sectionNames || []).length>0;
	metaProvider   = ["text", "iniInfo"];
}
