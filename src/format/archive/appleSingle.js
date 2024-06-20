import {Format} from "../../Format.js";

const _APPLESINGLE_MAGIC = ["Mac AppleSingle encoded", "AppleSingle encoded Macintosh file", /^AppleSingle$/, /^fmt\/(967|968)( |$)/];
export {_APPLESINGLE_MAGIC};

export class appleSingle extends Format
{
	name           = "AppleSingle";
	website        = "http://fileformats.archiveteam.org/wiki/AppleSingle";
	ext            = [".as"];
	forbidExtMatch = true;
	magic          = _APPLESINGLE_MAGIC;
	fallback       = true;
	converters     = ["unar[mac][skipMacBinaryConversion]", "deark[module:macrsrc]", "deark[module:applesd]"];
}
