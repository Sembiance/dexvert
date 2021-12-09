import {Format} from "../../Format.js";

export class mdf extends Format
{
	name       = "Alcohol 120% MDF Image";
	website    = "http://fileformats.archiveteam.org/wiki/MDF_and_MDS";
	ext        = [".mdf"];
	magic      = ["ISO 9660 CD image"];
	weakMagic  = true;
	priority   = this.PRIORITY.TOP;
	converters = ["MDFtoISO", "IsoBuster"];
}
