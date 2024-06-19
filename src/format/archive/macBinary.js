import {Format} from "../../Format.js";

const _APPLESINGLE_MAGIC = ["Mac AppleSingle encoded", "AppleSingle encoded Macintosh file", /^AppleSingle$/, /^fmt\/(967|968)( |$)/];
const _MACBINARY_MAGIC = ["Macintosh MacBinary", "MacBinary 2", "MacBinary II", "MacBinary, inited", "MacBinary 1", "MacBinary 3", ..._APPLESINGLE_MAGIC, /^MacBinary$/, / \(MacBinary\)$/, /^fmt\/(1762|1763)( |$)/];
export {_MACBINARY_MAGIC};

export class macBinary extends Format
{
	name           = "MacBinary/AppleSingle";
	website        = "http://fileformats.archiveteam.org/wiki/MacBinary";
	ext            = [".bin"];
	forbidExtMatch = true;
	magic          = _MACBINARY_MAGIC;
	fallback       = true;
	converters     = dexState =>
	{
		// MacBinary 1 files (preview.pix) are technically rsrc files, but only seem to work with macrssrc deark extraction
		const r = ["unar[mac][skipMacBinaryConversion]", "deark[module:macbinary]", "deark[module:macrsrc]"];
		if(dexState.hasMagics(_APPLESINGLE_MAGIC))
			r.push("deark[module:applesd]");
		
		return r;
	};
	notes = "We include MacBinary 1, 2, 3 and AppleSingle into this single format";
}
