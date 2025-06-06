import {Format} from "../../Format.js";

export class lucasfilmPicture extends Format
{
	name        = "Lucasfilm Picture";
	website     = "http://fileformats.archiveteam.org/wiki/Lucasfilm_picture";
	ext         = [".lff"];
	magic       = ["Prims :lff:"];
	converters  = ["nconvert[format:lff]]"];
}
