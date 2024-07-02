import {Format} from "../../Format.js";

export class windowsAutorun extends Format
{
	name           = "Windows Autorun File";
	website        = "http://fileformats.archiveteam.org/wiki/INF_(Windows)";
	ext            = [".nf"];
	filename       = [/^autorun.inf$/i];
	forbidExtMatch = true;
	magic          = ["Microsoft Windows Autorun file", "AutoRun Info", "INF Datei [AutoRun]", /^fmt\/331( |$)/];
	untouched      = true;
	metaProvider   = ["text"];
}
