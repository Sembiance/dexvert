import {Format} from "../../Format.js";
import {getMacBinaryMeta} from "../../identify.js";

const _MACBINARY_MAGIC = ["Macintosh MacBinary", "MacBinary 2", "MacBinary II", "MacBinary, inited", "MacBinary 1", "MacBinary 3", "deark: macbinary", "application/x-macbinary", /^MacBinary$/, /^MacBinary, .*19[89]\d, modified .*19[89]\d/, / \(MacBinary\)$/, /^fmt\/(1762|1763)( |$)/];
export {_MACBINARY_MAGIC};

export class macBinary extends Format
{
	name           = "MacBinary";
	website        = "http://fileformats.archiveteam.org/wiki/MacBinary";
	ext            = [".bin"];
	forbidExtMatch = true;
	magic          = _MACBINARY_MAGIC;
	idCheck        = async inputFile => !!(await getMacBinaryMeta(inputFile));
	fallback       = true;
	converters     = ["unar[mac][skipMacBinaryConversion]", "deark[module:macbinary]", "deark[module:macrsrc]"];	// MacBinary 1 files (preview.pix) are technically rsrc files, but only seem to work with macrssrc deark extraction
	notes          = "We include MacBinary 1, 2, 3 into this single format";
}
