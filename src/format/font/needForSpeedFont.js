import {Format} from "../../Format.js";

export class needForSpeedFont extends Format
{
	name           = "Need For Speed Font";
	ext            = [".ffn"];
	forbidExtMatch = true;
	magic          = ["The Need For Speed Font"];
	converters     = ["wuimg[format:eafnt]"];
}
