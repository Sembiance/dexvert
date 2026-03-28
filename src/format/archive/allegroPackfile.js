import {Format} from "../../Format.js";

export class allegroPackfile extends Format
{
	name           = "Allegro Packfile";
	website        = "http://fileformats.archiveteam.org/wiki/Allegro_packfile";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = [/^Allegro datafile/, "Allegro Packfile", "Allegro data", /^geArchive: DAT_SLHALL( |$)/];
	weakMagic      = [/^geArchive: DAT_SLHALL( |$)/];
	packed         = true;
	converters     = ["gameextractor[codes:DAT_SLHALL]", "pack"];
}
