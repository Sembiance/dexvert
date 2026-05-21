import {Format} from "../../Format.js";

export class epicTFP extends Format
{
	name        = "Epic TFP Document";
	website     = "https://www.vogons.org/viewtopic.php?f=5&t=35657&start=40";
	ext         = [".tfp"];
	magic       = ["Epic TFP format"];
	unsupported = true;	// only 65 unique files on discmaster, 90% are just ORDER forms for the games
	notes       = "Used in EPIC games. Supposedly can contain hyperlinks, graphics and animations all in a single document format";
}
