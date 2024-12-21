import {Format} from "../../Format.js";

export class indyPaint extends Format
{
	name       = "IndyPaint";
	website    = "http://fileformats.archiveteam.org/wiki/IndyPaint";
	ext        = [".tru"];
	magic      = ["IndyPaint bitmap"];
	converters = ["deark[module:indypaint]", "wuimg", "recoil2png"];
}
