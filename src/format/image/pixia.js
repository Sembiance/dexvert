import {Format} from "../../Format.js";

export class pixia extends Format
{
	name       = "Pixia";
	website    = "http://fileformats.archiveteam.org/wiki/Pixia";
	ext        = [".pxa"];
	magic      = ["Pixia bitmap", "Pixia :pxa:"];
	converters = ["nconvert[format:pxa]", "tomsViewer"];
}
