import {xu} from "xu";
import {Program} from "../../Program.js";

export class uniconvertor extends Program
{
	website = "https://sk1project.net/uc2/";
	package = "media-gfx/uniconvertor-appimage";
	flags   = {
		outType  : `Which type to convert to (svg || png). Default: svg`,
		autoCrop : "For SVG files, auto crop the result"
	};

	bin       = "uniconvertor";
	args      = r => [r.inFile(), `/out/out.${r.flags.outType || "svg"}`];
	osData    = ({timeout : xu.MINUTE*2});
	chain     = r => ((r.flags.outType || "svg")==="svg" ? `deDynamicSVG${r.flags.autoCrop ? "[autoCrop]" : ""}` : null);
	renameOut = true;
}
