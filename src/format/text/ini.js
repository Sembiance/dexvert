import {Format} from "../../Format.js";

export class ini extends Format
{
	name           = "INI File";
	website        = "http://fileformats.archiveteam.org/wiki/INI";
	ext            = [".ini", ".inf", ".cfg", ".conf", ".nfo"];
	forbidExtMatch = [".cfg", ".conf", ".nfo"];
	magic          = ["Generic INI configuration", "Windows desktop.ini", "InstallShield Setup config", "INF Datei", "Windows Initialization settings",
		"Microsoft Setup Toolkit for Windows files List", "LapLink 5 settings", "InstallShield Language Identifier", "TagInfo data", "TagInfo, ASCII text", "Delphi project Options"];
	priority       = this.PRIORITY.LOW;
	untouched      = dexState => dexState.meta.valid && (dexState.meta.sectionNames || []).length>0;
	metaProvider   = ["text", "iniInfo"];
}
