import {Format} from "../../Format.js";

export class compressedFileLibrary3 extends Format
{
	name       = "Compressed File Library 3";
	website    = "http://fileformats.archiveteam.org/wiki/CFL";
	ext        = [".cfz", ".cfl"];
	magic      = ["Compressed File Library 3 compressed data", "Archive: Jari Comppa's Compressed File Library 3 file (.CFL)"];
	converters = ["uncfl"];
}
