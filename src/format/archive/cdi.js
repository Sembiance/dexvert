import {Format} from "../../Format.js";

export class cdi extends Format
{
	name         = "Compact Disc-Interactive";
	website      = "http://fileformats.archiveteam.org/wiki/Cd-i";
	ext          = [".bin"];
	weakExt      = true;
	magic        = ["CD-I disk image"];
	keepFilename = true;
	auxFiles     = (input, otherFiles) => otherFiles.filter(file => file.ext.toLowerCase()===".cue");	// just grab all cue files
	converters   = ["IsoBuster"];
}
