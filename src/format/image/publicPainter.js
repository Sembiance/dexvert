import {xu} from "xu";
import {Format} from "../../Format.js";

export class publicPainter extends Format
{
	name       = "Public  Painter";
	website    = "http://fileformats.archiveteam.org/wiki/Public_Painter";
	ext        = [".cmp"];
	priority   = this.PRIORITY.LOW;
	idCheck    = inputFile => inputFile.size<(xu.KB*32);	// Pretty weak match, just an extension, so do a little sanity checking on file size. Haven't encountered any larger than 30k, so restrict to 32k or less
	converters = ["recoil2png"];
}
