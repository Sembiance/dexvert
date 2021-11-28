import {Format} from "../../Format.js";

export class samCoupeMode4 extends Format
{
	name       = "SAM Coupe Mode 4";
	website    = "http://fileformats.archiveteam.org/wiki/SAM_Coupe_Mode_4";
	ext        = [".ss4", ".scs4"];
	fileSize   = 24617;
	converters = ["recoil2png"];
}
