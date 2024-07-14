import {Format} from "../../Format.js";

export class ini extends Format
{
	name           = "INI File";
	website        = "http://fileformats.archiveteam.org/wiki/INI";
	ext            = [".ini", ".inf", ".cfg", ".conf", ".nfo"];
	forbidExtMatch = [".cfg", ".conf", ".nfo"];
	magic          = ["Generic INI configuration", "Windows desktop.ini", "InstallShield Setup config", "INF Datei", "Windows Initialization settings",
		"Windows Dial-Up Networking configuration", "Microsoft Setup Toolkit for Windows files List", "LapLink 5 settings", "InstallShield Language Identifier", "TagInfo data", "TagInfo, ASCII text", "Delphi project Options", "BRIEF session info",
		"Windows Explorer Command Shell File", "Windows Explorer Shell Command File", "AOL Modem parameters"];
	priority       = this.PRIORITY.LOW;
	untouched      = dexState => dexState.meta.valid && (dexState.meta.sectionNames || []).length>0;
	metaProvider   = ["text", "iniInfo"];
}
