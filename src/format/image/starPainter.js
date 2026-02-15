import {Format} from "../../Format.js";

export class starPainter extends Format
{
	name       = "Star Painter";
	website    = "http://fileformats.archiveteam.org/wiki/Star_Painter";
	ext        = [".gr", ".cs", ".zs"];
	converters = ["recoil2png[format:GR,ZS,CS]"];
}
