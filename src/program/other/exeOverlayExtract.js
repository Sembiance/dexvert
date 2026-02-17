import {xu} from "xu";
import {Program} from "../../Program.js";
import {extractEXEOverlay} from "../../exeOverlayUtil.js";

export class exeOverlayExtract extends Program
{
	website = "https://github.com/Sembiance/dexvert";
	loc     = "local";
	flags   = {
		chainAs : "Chain to dexvert as this format",
		ext     : "Output file extension"
	};
	exec      = async r => await extractEXEOverlay(r.inFile({absolute : true}), await r.outFile(`outfile${r.flags.ext || ""}`, {absolute : true}));
	chain     = r => (r.flags.chainAs ? `dexvert[asFormat:${r.flags.chainAs}]` : null);
	renameOut = true;
}
