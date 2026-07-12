import {Format} from "../../Format.js";

export class themepak extends Format
{
	name           = "THEMEPAK Installer";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["Installer: THEMEPAK"];
	converters     = ["vibeExtract"];
}
