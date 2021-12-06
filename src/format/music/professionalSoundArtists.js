import {Format} from "../../Format.js";

export class professionalSoundArtists extends Format
{
	name         = "Professional Sound Artists Module";
	ext          = ["psa"];
	magic        = ["Professional Sound Artists module", "PSA archive data"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
