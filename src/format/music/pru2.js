import {Format} from "../../Format.js";

export class pru2 extends Format
{
	name         = "Prorunner Module";
	website      = "http://fileformats.archiveteam.org/wiki/Prorunner";
	ext          = [".pru2"];
	magic        = ["Prorunner 2.0 Music"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp"];
}
