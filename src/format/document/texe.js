import {Format} from "../../Format.js";

const _TEXE_MAGIC = ["TEXE generated doc viewer"];
export {_TEXE_MAGIC};

export class texe extends Format
{
	name           = "TEXE";
	website        = "http://fileformats.archiveteam.org/wiki/TEXE";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = _TEXE_MAGIC;
	converters     = ["textract"];
}
