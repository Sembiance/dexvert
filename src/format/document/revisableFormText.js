import {Format} from "../../Format.js";

export class revisableFormText extends Format
{
	name           = "IBM Revisable-Form Text";
	website        = "http://fileformats.archiveteam.org/wiki/RFT";
	ext            = [".rft", ".dca", ".fft"];
	forbidExtMatch = true;
	magic          = [/Revisable Form Text/, /^x-fmt\/148( |$)/];
	converters     = ["fileMerlin", "word97"];
}
