import {Format} from "../../Format.js";

export class msvcRes extends Format
{
	name           = "MSVC Resource File";
	ext            = [".res"];
	forbidExtMatch = true;
	magic          = ["MSVC .res", "Windows compiled resource"];
	notes          = "There is probably a better way to open these, maybe visual studio?";
	converters     = ["strings"];
}
