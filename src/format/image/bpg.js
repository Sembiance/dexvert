import {Format} from "../../Format.js";

export class bpg extends Format
{
	name       = "Better Portable Graphics";
	website    = "http://fileformats.archiveteam.org/wiki/BPG";
	ext        = [".bpg"];
	mimeType   = "image/x-bpg";
	magic      = ["Better Portable Graphics", "BPG (Better Portable Graphics)"];
	notes      = "Some BPG files are animated, but dexvert doesn't support these yet. All BPG files are just converted into single PNG Files.";
	converters = ["bpgdec"]
}
