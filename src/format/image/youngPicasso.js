import {Format} from "../../Format.js";

export class youngPicasso extends Format
{
	name           = "ArtMaster88";
	website        = "http://fileformats.archiveteam.org/wiki/Young_Picasso";
	ext            = [".yp"];
	forbidExtMatch = true;
	magic          = ["Young Picasso"];
	converters     = ["deark[module:young_picasso]"];
}
