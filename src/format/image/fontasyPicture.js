import {Format} from "../../Format.js";

export class fontasyPicture extends Format
{
	name           = "Fontasy Picture";
	website        = "http://fileformats.archiveteam.org/wiki/FONTASY_graphics";
	ext            = [".pic", ".tem"];
	forbidExtMatch = true;
	magic          = ["FONTASY Picture"];
	converters     = ["iconvertDOS[format:fontasyPIC]"];
}
