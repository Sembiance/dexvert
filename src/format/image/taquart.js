import {Format} from "../../Format.js";

export class taquart extends Format
{
	name       = "Taquart Interlace Picture";
	website    = "http://fileformats.archiveteam.org/wiki/Taquart_Interlace_Picture";
	ext        = [".tip"];
	magic      = ["Taquart Interlace Picture bitmap"];
	converters = ["recoil2png"];
}
