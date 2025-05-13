import {Format} from "../../Format.js";

export class mmfwMoviesArchive extends Format
{
	name           = "MMFW Movies Archive";
	ext            = [".mov"];
	forbidExtMatch = true;
	magic          = ["MMFW Movies Archive"];
	keepFilename   = true;
	converters     = ["mmvid_extractor"];
}
