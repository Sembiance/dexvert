import {Format} from "../../Format.js";

export class mmfwMoviesArchive extends Format
{
	name           = "MMFW Movies Archive";
	ext            = [".mov"];
	forbidExtMatch = true;
	magic          = ["MMFW Movies Archive"];
	keepFilename   = true;
	converters     = ["therock_decoder"];	// WARNING: This decoder currently only supports sciguy.mov  see it's JS for more notes
}
