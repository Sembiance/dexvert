import {Format} from "../../Format.js";

export class shandaBambook extends Format
{
	name           = "Shanda Bambook";
	website        = "http://fileformats.archiveteam.org/wiki/Shanda_Bambook";
	ext            = [".snb", ".bek"];
	magic          = ["Shanda Bambook eBook"];
	converters     = ["ebook_convert"];
}
