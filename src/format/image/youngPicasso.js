import {Format} from "../../Format.js";

export class youngPicasso extends Format
{
	name           = "Young Picasso";
	website        = "http://fileformats.archiveteam.org/wiki/Young_Picasso";
	ext            = [".yp"];
	forbidExtMatch = true;
	magic          = ["Young Picasso", "deark: young_picasso"];
	converters     = ["deark[module:young_picasso]"];
}
