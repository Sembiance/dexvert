import {Format} from "../../Format.js";

export class sidMon2 extends Format
{
	name         = "SidMon II Module";
	website      = "http://fileformats.archiveteam.org/wiki/Sidmon";
	ext          = [".sid2"];
	magic        = ["Sidmon II module", "Sidmon 2.0 Module sound file"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
