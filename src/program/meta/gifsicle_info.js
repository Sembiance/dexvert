import {Program} from "../../Program.js";

export class gifsicle_info extends Program
{
	website = "https://www.lcdf.org/~eddietwo/gifsicle/";
	package = "media-gfx/gifsicle";
	bin     = "gifsicle";
	args    = r => ["-I", r.inFile()];
	post    = r =>
	{
		if(r.stdout.trim().split("\n").some(line => line.trim().match(/^\* .+ \d+ images$/)))
			r.meta.animated = true;
	};
}
