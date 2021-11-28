import {Format} from "../../Format.js";

export class pgx extends Format
{
	name       = "Portfolio PGX";
	website    = "http://fileformats.archiveteam.org/wiki/PGX_(Portfolio)";
	ext        = [".pgx"];
	magic      = ["Portfolio PGX bitmap"];
	notes      = "Sometimes instead of a single bitmap, it's multiple frames to a animation which we then convert into an GIF";
	converters = ["deark -> dexvert[asFormat:image/pgc] -> *joinAsGIF"];
}
