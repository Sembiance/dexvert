import {Format} from "../../Format.js";

export class figlet extends Format
{
	name       = "FIGlet Font";
	website    = "http://fileformats.archiveteam.org/wiki/FIGlet_font";
	ext        = [".flf"];
	magic      = ["FIGfont", "FIGlet font"];
	converters = ["figlet"];
}
