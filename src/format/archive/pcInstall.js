import {Format} from "../../Format.js";

export class pcInstall extends Format
{
	name           = "PCInstall Installer";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Installer: PCInstall"];
	converters     = ["vibeExtract"];
}
