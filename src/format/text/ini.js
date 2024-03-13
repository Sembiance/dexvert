import {Format} from "../../Format.js";

export class ini extends Format
{
	name           = "INI File";
	website        = "http://fileformats.archiveteam.org/wiki/INI";
	ext            = [".ini", ".inf", ".cfg", ".conf", ".nfo"];
	forbidExtMatch = [".cfg", ".conf", ".nfo"];
	magic          = ["Generic INI configuration", "Windows desktop.ini"];
	priority       = this.PRIORITY.LOW;
	untouched      = dexState => dexState.meta.valid && (dexState.meta.sectionNames || []).length>0;
	metaProvider   = ["text", "iniInfo"];
}
