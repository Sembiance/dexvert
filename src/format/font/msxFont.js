import {Format} from "../../Format.js";

export class msxFont extends Format
{
	name           = "MSX Alfabeto/Graphos III Font";
	ext            = [".alf"];
	forbidExtMatch = true;
	magic          = ["MSX Font"];
	converters     = ["wuimg[format:msxalf]"];
}
