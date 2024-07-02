import {Format} from "../../Format.js";

export class windowsProgramGroup extends Format
{
	name           = "Windows Program Group";
	website        = "http://fileformats.archiveteam.org/wiki/Windows_program_group";
	ext            = [".grp"];
	forbidExtMatch = true;
	magic          = ["Windows Program Manager Group", "Windows 3.x .GRP file", "Windows 3.x Gruppendatei", "MS Windows 3.1 group files"];
	converters     = ["strings"];
}
