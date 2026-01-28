import {Format} from "../../Format.js";

export class rtPatchSFX extends Format
{
	name           = "RTPatch Self-Extracting Archive";
	website        = "http://justsolve.archiveteam.org/wiki/RTPatch";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = ["RTPatch SFX"];
	converters     = ["dosEXEExtract"];
}
