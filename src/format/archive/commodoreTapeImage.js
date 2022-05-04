import {Format} from "../../Format.js";

export class commodoreTapeImage extends Format
{
	name    = "Commodore Tape Image";
	website = "http://fileformats.archiveteam.org/wiki/T64";
	ext     = [".t64"];
	magic   = ["T64 Tape Image", "Commodore 64 Tape container", /^fmt\/820( |$)/];
	
	// Alternatively we could use c1541 to convert the tape image to a d64 image and then process it through c1541. See: https://immerhax.com/?p=136
	converters = ["DirMaster"];
}
