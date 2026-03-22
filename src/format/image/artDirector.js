import {Format} from "../../Format.js";

export class artDirector extends Format
{
	name       = "Art Director";
	website    = "http://fileformats.archiveteam.org/wiki/Art_Director";
	ext        = [".art"];
	mimeType   = "image/x-art-director";
	magic      = ["Art Director :artdir:"];
	fileSize   = 32512;
	converters = ["recoil2png[format:ART.ArtDirector]", `abydosconvert[format:${this.mimeType}]`, "nconvert[format:artdir]"];
}
