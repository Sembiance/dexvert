import {Format} from "../../Format.js";

export class kro extends Format
{
	name       = "Kolor Raw";
	website    = "http://fileformats.archiveteam.org/wiki/Kolor_Raw";
	ext        = [".kro"];
	magic      = ["Kolor Raw image format"];
	converters = ["nconvert", "wuimg", "tomsViewer"];
}
