import {Format} from "../../Format.js";

export class windowsProgramGroup extends Format
{
	name           = "Windows Program Group";
	ext            = [".grp"];
	forbidExtMatch = true;
	magic          = ["Windows Program Manager Group", "Windows 3.x .GRP file"];
	converters     = ["strings"];
}
