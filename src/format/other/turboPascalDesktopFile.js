import {Format} from "../../Format.js";

export class turboPascalDesktopFile extends Format
{
	name           = "Turbo Pascal Desktop File";
	ext            = [".dsk"];
	forbidExtMatch = true;
	magic          = ["Turbo Pascal Desktop"];
	converters     = ["strings"];
}
