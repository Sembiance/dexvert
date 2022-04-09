import {xu} from "xu";
import {Program} from "../../Program.js";

export class uniconvertor extends Program
{
	website = "https://sk1project.net/uc2/";
	package = "media-gfx/uniconvertor";
	flags   = {
		outType : `Which type to convert to (svg || png). Default: svg`
	};

	loc       = "gentoo";	// when running LOTS of copies at once, the AppImage often fails, so we run on gentoo VM to ensure only 1 conversion at once
	bin       = "uniconvertor";
	args      = r => [r.inFile(), `/out/out.${r.flags.outType || "svg"}`];
	qemuData  = ({timeout : xu.MINUTE*2});
	chain     = r => ((r.flags.outType || "svg")==="svg" ? "deDynamicSVG" : null);
	renameOut = true;
}
