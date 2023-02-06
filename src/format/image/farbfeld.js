import {Format} from "../../Format.js";

export class farbfeld extends Format
{
	name       = "Farbfeld";
	website    = "http://fileformats.archiveteam.org/wiki/Farbfeld";
	ext        = [".ff"];
	mimeType   = "image/x-farbfeld";
	magic      = [/[Ff]arbfeld ([Ii]mage|bitmap)/, /^fmt\/1133( |$)/];
	converters = ["deark", `abydosconvert[format:${this.mimeType}]`];
	verify     = ({meta}) => meta.height>1 && meta.width>1;
}
