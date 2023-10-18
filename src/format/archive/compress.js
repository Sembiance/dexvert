import {Format} from "../../Format.js";

export class compress extends Format
{
	name       = "Compress Compressed (Unix)";
	website    = "http://fileformats.archiveteam.org/wiki/Compress";
	ext        = [".z", ".tz", ".taz"];
	magic      = ["Compress compressed data", "compress'd data", "UNIX compressed data", "Z: Compress"];
	packed     = true;
	converters = ["ancient", "gunzip", "deark[module:compress]", "xfdDecrunch", "izArc"];
}
