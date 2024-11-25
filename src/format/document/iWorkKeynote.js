import {Format} from "../../Format.js";

export class iWorkKeynote extends Format
{
	name           = "Apple iWork Keynote";
	ext            = [".key"];
	forbidExtMatch = true;
	magic          = [/^fmt\/646( |$)/];
	converters     = ["soffice[format:AppleKeynote]"];
}
