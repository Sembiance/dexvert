import {Format} from "../../Format.js";

export class webshotsPicture extends Format
{
	name       = "Webshots Picture";
	website    = "http://fileformats.archiveteam.org/wiki/Webshots_picture";
	ext        = [".wb1", ".wbz", ".wbd", ".wbc", ".wbp"];
	magic      = ["Webshots Image"];
	converters = ["nconvert"];
}
