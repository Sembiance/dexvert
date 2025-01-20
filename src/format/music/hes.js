import {Format} from "../../Format.js";

export class hes extends Format
{
	name         = "Hudson Entertainment System Sound Format";
	website      = "http://fileformats.archiveteam.org/wiki/HES";
	ext          = [".hes"];
	magic        = ["Hudson Entertainment System Sound Format dump"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123[largeQuota][trimSilence]"];
}
