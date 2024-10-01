import {Format} from "../../Format.js";

export class interplayACM extends Format
{
	name           = "Interplay Compressed Audio";
	website        = "http://fileformats.archiveteam.org/wiki/Interplay_ACM";
	ext            = [".acm"];
	magic          = ["Interplay Compressed Audio Format", "Interplay ACM (acm)"];
	converters     = ["zxtune123", "acm2wav"];
}
