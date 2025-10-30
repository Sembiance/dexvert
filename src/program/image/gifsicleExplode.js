import {Program} from "../../Program.js";

export class gifsicleExplode extends Program
{
	website   = "https://www.lcdf.org/~eddietwo/gifsicle/";
	package   = "media-gfx/gifsicle";
	bin       = "gifsicle";
	args      = r => ["--explode", r.inFile()];
	cwd       = r => r.outDir();
	renameOut = true;
}
