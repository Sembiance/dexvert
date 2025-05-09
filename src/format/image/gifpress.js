import {Format} from "../../Format.js";

export class gifpress extends Format
{
	name           = "Gifpress Compressed GIF";
	website        = "http://fileformats.archiveteam.org/wiki/Gifpress";
	ext            = [".gps"];
	forbidExtMatch = true;
	magic          = ["Gifpress GIF", "Gifpress compressed GIF"];
	weakMagic      = true;
	converters     = ["gifpress"];
}
