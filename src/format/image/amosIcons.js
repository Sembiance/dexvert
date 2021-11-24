import {Format} from "../../Format.js";

export class amosIcons extends Format
{
	name       = "AMOS Icons Bank";
	website    = "http://fileformats.archiveteam.org/wiki/AMOS_Icon_Bank";
	ext        = [".abk"];
	mimeType   = "image/x-amos-iconbank";
	magic      = ["AMOS Icons Bank"];
	converters = ["deark"]
}
