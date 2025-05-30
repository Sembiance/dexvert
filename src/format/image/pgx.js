import {xu} from "xu";
import {Format} from "../../Format.js";

export class pgx extends Format
{
	name       = "Portfolio PGX";
	website    = "http://fileformats.archiveteam.org/wiki/PGX_(Portfolio)";
	ext        = [".pgx"];
	magic      = ["Portfolio PGX bitmap", "deark: pgx (PGX (Portfolio Animation))"];
	notes      = xu.trim`
		Sometimes instead of a single bitmap, it's multiple frames to a animation which we then convert into an GIF.
		Each PGC file within the PGX specifies have how long to delay between each frame, so we could make a better GIF: https://www.idealine.info/portfolio/library/text/pgxspec.txt`;
	converters = ["deark[module:pgx] -> dexvert[asFormat:image/pgc] -> *ffmpeg[fps:8][outType:gif]"];
}
