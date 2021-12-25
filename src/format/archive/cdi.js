import {Format} from "../../Format.js";

export class cdi extends Format
{
	name           = "Compact Disc-Interactive";
	website        = "http://fileformats.archiveteam.org/wiki/Cd-i";
	ext            = [".bin"];
	forbidExtMatch = true;	// .bin is way too common, no need to launch IsoBuster for every .bin file. Still, if I discover the magic isn't 100%, then I can add it back in
	magic          = ["CD-I disk image"];
	keepFilename   = true;
	auxFiles       = (input, otherFiles) => otherFiles.filter(file => file.ext.toLowerCase()===".cue");	// just grab all cue files
	converters     = ["IsoBuster"];
}
