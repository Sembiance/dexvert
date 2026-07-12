import {Format} from "../../Format.js";

export class gpInstall extends Format
{
	name           = "GPInstall Installer";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Installer: GPInstall"];
	converters     = ["vibeExtract"];
}
