import {Format} from "../../Format.js";

export class electronicArtsFont extends Format
{
	name           = "Electronic Arts Font";
	ext            = [".ffn"];
	forbidExtMatch = true;
	magic          = ["Electronic Arts Font (generic)", "FIFA game serie Font"];
	converters     = ["wuimg[format:eafnt]"];
}
