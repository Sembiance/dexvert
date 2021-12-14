import {Format} from "../../Format.js";

export class revisableFormText extends Format
{
	name           = "IBM Revisable-Form Text";
	ext            = [".rft", ".dca"];
	forbidExtMatch = true;
	magic          = [/Revisable Form Text/];
	converters     =  ["fileMerlin", "word97"];
}
