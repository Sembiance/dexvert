import {Format} from "../../Format.js";

export class allegroPackfile extends Format
{
	name           = "Allegro Packfile";
	website        = "http://fileformats.archiveteam.org/wiki/Allegro_packfile";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = ["Allegro datafile", "Allegro Packfile", "Allegro data"];
	packed         = true;
	converters     = ["pack"];
}
