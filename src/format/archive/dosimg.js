import {Format} from "../../Format.js";

export class dosimg extends Format
{
	name           = "DOSIMG Disk Image";
	website        = "http://fileformats.archiveteam.org/wiki/IMG_(DOSIMG)";
	ext            = [".img"];
	forbidExtMatch = true;
	magic          = ["DOSIMG disk image", "HD-Copy disk image"];
	converters     = ["aaru"];
}
