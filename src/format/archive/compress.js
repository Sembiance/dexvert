import {Format} from "../../Format.js";

export class compress extends Format
{
	name       = "Compress Compressed (Unix)";
	website    = "http://fileformats.archiveteam.org/wiki/Compress_(Unix)";
	ext        = [".z", ".tz", ".taz"];
	magic      = [
		"Compress compressed data", "compress'd data", "UNIX compressed data", "Z: Compress", "COMP16 Archiv gefunden", "bar archive compress-compressed data", "Archive: Compress", "application/x-compress", /^compress-compressed/, /^Compress$/,
		/^deark: compress$/,
		/^fmt\/1671( |$)/
	];
	idMeta     = ({macFileType, macFileCreator}) => (macFileType==="Com+" && macFileCreator==="TeX+") || (macFileType==="COMP" && macFileCreator==="MPS ") || (macFileType==="ZIVM" && macFileCreator==="LZIV");
	packed     = true;
	converters = ["ancient", "gunzip", "deark[module:compress]", "unar", "xfdDecrunch", "izArc[matchType:magic]"];
}
