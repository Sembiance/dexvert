import {Format} from "../../Format.js";

export class taquart extends Format
{
	name       = "Taquart Interlace Picture";
	website    = "http://fileformats.archiveteam.org/wiki/Taquart_Interlace_Picture";
	ext        = [".tip"];
	magic      = ["Taquart Interlace Picture bitmap", /^fmt\/1589( |$)/];
	converters = ["recoil2png"];
}
