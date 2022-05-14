import {Format} from "../../Format.js";

export class deskMate extends Format
{
	name           = "DeskMate Document";
	ext            = [".doc"];
	forbidExtMatch = true;
	magic          = ["DeskMate document"];
	converters     = ["strings"];
}
