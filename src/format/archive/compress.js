import {Format} from "../../Format.js";

export class compress extends Format
{
	name       = "Compress Compressed (Unix)";
	website    = "http://fileformats.archiveteam.org/wiki/Compress_(Unix)";
	ext        = [".z", ".tz", ".taz"];
	magic      = ["Compress compressed data", "compress'd data", "UNIX compressed data", "Z: Compress", "COMP16 Archiv gefunden", "Archive: Compress", /^compress-compressed data$/, /^Compress$/, /^fmt\/1671( |$)/];
	packed     = true;
	converters = ["ancient", "gunzip", "deark[module:compress]", "unar", "xfdDecrunch", "izArc"];
}
