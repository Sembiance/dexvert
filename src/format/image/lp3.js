import {Format} from "../../Format.js";

export class lp3 extends Format
{
	name       = "Logo-Painter";
	website    = "http://fileformats.archiveteam.org/wiki/Logo-Painter";
	ext        = [".lp3"];
	magic      = ["Picasso 64 Image"];
	weakMagic  = true;
	converters = ["recoil2png", "view64"];
}
