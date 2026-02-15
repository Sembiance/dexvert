import {Format} from "../../Format.js";

export class artDirector extends Format
{
	name       = "Art Director";
	website    = "http://fileformats.archiveteam.org/wiki/Art_Director";
	ext        = [".art"];
	magic      = ["Art Director :artdir:"];
	fileSize   = 32512;
	converters = ["recoil2png[format:ART.ArtDirector]", "nconvert[format:artdir]"];
}
