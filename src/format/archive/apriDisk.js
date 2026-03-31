import {Format} from "../../Format.js";

export class apriDisk extends Format
{
	name           = "ApriDisk";
	website        = "http://fileformats.archiveteam.org/wiki/ApriDisk";
	ext            = [".dsk"];
	forbidExtMatch = true;
	magic          = ["ACT Apricot disk image"];
	converters     = ["dskconv[inType:APRIDISK]"];
}
