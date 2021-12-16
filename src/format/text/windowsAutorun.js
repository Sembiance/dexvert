import {Format} from "../../Format.js";

export class windowsAutorun extends Format
{
	name           = "Windows Autorun File";
	website        = "http://fileformats.archiveteam.org/wiki/INF_(Windows)";
	ext            = [".nf"];
	filename       = [/^autorun.inf$/i];
	forbidExtMatch = true;
	magic          = ["Microsoft Windows Autorun file", "AutoRun Info"];
	untouched      = true;
	metaProvider   = ["text"];
}
