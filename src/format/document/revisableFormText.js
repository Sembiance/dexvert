import {Format} from "../../Format.js";

export class revisableFormText extends Format
{
	name           = "IBM Revisable-Form Text";
	website        = "http://fileformats.archiveteam.org/wiki/RFT";
	ext            = [".rft", ".dca", ".fft"];
	forbidExtMatch = true;
	magic          = [/Revisable Form Text/];
	converters     = ["fileMerlin", "word97"];
}
