import {Format} from "../../Format.js";

export class proRunner extends Format
{
	name         = "ProRunner Module";
	website      = "http://fileformats.archiveteam.org/wiki/Prorunner";
	ext          = [".pru2", ".pru1", ".pr1", ".pr2"];
	magic        = ["Prorunner 2.0 Music"];
	metaProvider = ["musicInfo"];
	converters   = ["xmp", "uade123"];
}
