import {xu} from "xu";
import {Program} from "../../Program.js";

export class uniconvertor extends Program
{
	website = "https://sk1project.net/uc2/";
	package = "media-gfx/uniconvertor";
	flags   = {
		outType : `Which type to convert to (svg || png). Default: svg`
	};

	bin        = "uniconvertor";
	args       = async r => [r.inFile(), await r.outFile(`out.${r.flags.outType || "svg"}`)];
	runOptions = ({timeout : xu.MINUTE*3});
	renameOut  = true;
	chain      = r => ((r.flags.outType || "svg")==="svg" ? "deDynamicSVG" : null);
}
