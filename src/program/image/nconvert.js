import {xu} from "xu";
import {Program} from "../../Program.js";
import * as path from "https://deno.land/std@0.111.0/path/mod.ts";

export class nconvert extends Program
{
	website       = "https://www.xnview.com/en/nconvert/";
	gentooPackage = "media-gfx/nconvert";
	gentooOverlay = "dexvert";
	flags         =
	{
		format : "Which nconvert format to use for conversion. For list run `nconvert -help` Default: Let nconvert decide"
	};

	bin    = "nconvert";
	outExt = ".png";
	args   = r => [...(r.flags.format ? ["-in", r.flags.format] : []), "-out", "png", "-o", path.join(r.f.outDir.rel, "out.png"), r.f.input.rel]
}
