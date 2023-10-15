import {Format} from "../../Format.js";

export class quasijarus extends Format
{
	name       = "Quasijarus Strong Compressed";
	website    = "http://fileformats.archiveteam.org/wiki/Quasijarus_Strong_Compression";
	ext        = [".z"];
	magic      = ["Quasijarus strong compressed data", "Quasijarus Strong Compression compressed data", "Z: Quasijarus Strong Compression"];
	packed     = true;
	converters = ["ancient"];
}
