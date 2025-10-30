import {Format} from "../../Format.js";

export class aldusPersuasionPlayerFile extends Format
{
	name           = "Aldus Persuasion Player File";
	ext            = [".ppf"];
	forbidExtMatch = true;
	magic          = [/^fmt\/1708( |$)/];	// NOTE: If I find more magics later, ensure I update format/image/gif.js confidenceAdjust too
	converters     = ["gifsicleExplode -> *img2pdf"];
}
