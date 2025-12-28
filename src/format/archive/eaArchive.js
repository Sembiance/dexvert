import {Format} from "../../Format.js";

export class eaArchive extends Format
{
	name           = "EA Archive";
	website        = "http://fileformats.archiveteam.org/wiki/EA_archive";
	ext            = [".ea", ".pea"];
	forbidExtMatch = true;
	magic          = ["deark: ea_arch"];
	converters     = ["deark[module:ea_arch]"];
}
