import {xu} from "xu";
import {Format} from "../../Format.js";

export class publicPainter extends Format
{
	name       = "Public  Painter";
	website    = "http://fileformats.archiveteam.org/wiki/Public_Painter";
	ext        = [".cmp"];
	idCheck    = inputFile => inputFile.size<(xu.KB*100);	// Pretty weak match, just an extension, so do a little sanity checking on file size. Haven't encountered any larger than 30k, so restrict to 100k or less
	converters = ["recoil2png"];
}
