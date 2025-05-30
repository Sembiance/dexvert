import {Format} from "../../Format.js";

export class scoCompress extends Format
{
	name       = "SCO Compress";
	website    = "http://fileformats.archiveteam.org/wiki/SCO_compress_LZH";
	safeExt    = ".gz";
	magic      = ["SCO compress", "SCO Compress", "Archive: SCO", "deark: compress_lzh"];
	packed     = true;
	converters = ["gunzip", "deark[module:compress_lzh]", "ancient"];
}
