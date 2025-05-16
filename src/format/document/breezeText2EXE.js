import {Format} from "../../Format.js";

export class breezeText2EXE extends Format
{
	name           = "Breeze/TextLife Text-to-Executable";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["16bit EXE Breeze text to Executable (generic)"];
	converters     = ["deark[module:textlife][opt:text:encconv=0]"];
}
