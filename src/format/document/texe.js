import {Format} from "../../Format.js";

export class texe extends Format
{
	name           = "TEXE";
	website        = "http://fileformats.archiveteam.org/wiki/TEXE";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["TEXE generated doc viewer"];
	converters     = ["textract"];
}
