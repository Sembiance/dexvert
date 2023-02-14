import {Format} from "../../Format.js";

export class cramFS extends Format
{
	name       = "Compressed ROM File System";
	website    = "http://fileformats.archiveteam.org/wiki/Cramfs";
	magic      = ["Linux Compressed ROM File System", "Cramfs ROM filesystem package"];
	converters = ["sevenZip"];
}
