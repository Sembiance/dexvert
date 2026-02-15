import {Format} from "../../Format.js";

export class samCoupeMode4 extends Format
{
	name       = "SAM Coupe Mode 4";
	website    = "http://fileformats.archiveteam.org/wiki/SAM_Coupé_Mode_4";
	ext        = [".ss4", ".scs4"];
	fileSize   = [24617, 25113];
	converters = ["recoil2png[format:SS4.Ss4]"];
}
