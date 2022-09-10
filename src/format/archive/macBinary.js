import {Format} from "../../Format.js";

const _MACBINARY_MAGIC = ["MacBinary 2", "MacBinary II", "MacBinary, inited", "MacBinary 1", "Mac AppleSingle encoded"];
export {_MACBINARY_MAGIC};

export class macBinary extends Format
{
	name           = "MacBinary";
	website        = "http://fileformats.archiveteam.org/wiki/MacBinary";
	ext            = [".bin"];
	forbidExtMatch = true;
	magic          = _MACBINARY_MAGIC;
	fallback       = true;
	converters     = ["unar[mac]", "deark[module:macbinary]", "deark[module:macrsrc]"];	// MacBinary 1 files (preview.pix) are technically rsrc files, but only seem to work with macrssrc deark extraction
}
