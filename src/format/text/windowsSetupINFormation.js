import {Format} from "../../Format.js";

export class windowsSetupINFormation extends Format
{
	name         = "Windows Setup INFormation";
	website      = "http://fileformats.archiveteam.org/wiki/INF_(Windows)";
	magic        = ["Windows setup INFormation", "Windows driver setup Information", "INF Datei [Version]", /^x-fmt\/420( |$)/];
	untouched    = true;
	metaProvider = ["text"];
}
