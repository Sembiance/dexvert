import {Format} from "../../Format.js";

export class binscii extends Format
{
	name       = "BinSCII";
	website    = "http://fileformats.archiveteam.org/wiki/BinSCII";
	ext        = [".bsc", ".bsq"];
	magic      = ["BinSCII", "binscii"];
	converters = ["binsciiPrepare -> deark[module:binscii]"];
}
