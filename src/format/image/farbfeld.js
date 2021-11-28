import {Format} from "../../Format.js";

export class farbfeld extends Format
{
	name       = "Farbfeld";
	website    = "http://fileformats.archiveteam.org/wiki/Farbfeld";
	ext        = [".ff"];
	mimeType   = "image/x-farbfeld";
	magic      = [/[Ff]arbfeld ([Ii]mage|bitmap)/];	// eslint-disable-line prefer-named-capture-group
	converters = ["deark", `abydosconvert[format:${this.mimeType}]`];
}
