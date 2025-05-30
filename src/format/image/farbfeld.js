import {Format} from "../../Format.js";

export class farbfeld extends Format
{
	name       = "Farbfeld";
	website    = "http://fileformats.archiveteam.org/wiki/Farbfeld";
	ext        = [".ff"];
	mimeType   = "image/x-farbfeld";
	magic      = [/[Ff]arbfeld ([Ii]mage|bitmap)/, "deark: farbfeld", /^fmt\/1133( |$)/];
	converters = ["deark[module:farbfeld]", "wuimg", `abydosconvert[format:${this.mimeType}]`];
	verify     = ({meta}) => meta.height>1 && meta.width>1;
}
