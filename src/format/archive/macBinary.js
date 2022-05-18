import {Format} from "../../Format.js";

export class macBinary extends Format
{
	name           = "MacBinary";
	website        = "http://fileformats.archiveteam.org/wiki/MacBinary";
	magic          = ["MacBinary 2", "MacBinary II", "MacBinary, inited", "MacBinary 1", "Mac AppleSingle encoded"];
	ext            = [".bin"];
	forbidExtMatch = true;
	fallback       = true;
	converters     = ["unar[mac]", "deark[module:macbinary]"];
}
