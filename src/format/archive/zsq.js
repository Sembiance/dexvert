import {Format} from "../../Format.js";

export class zsq extends Format
{
	name       = "ZSQ";
	website    = "http://fileformats.archiveteam.org/wiki/ZSQ_(LZW_compression)";
	ext        = [".zzz"];
	magic      = ["ZSQ compressed data"];
	packed     = true;
	converters = ["deark[module:zsq]"];
}
