import {Format} from "../../Format.js";

export class paintworks extends Format
{
	name       = "Paintworks";
	website    = "http://fileformats.archiveteam.org/wiki/Paintworks";
	ext        = [".cl0", ".sc0", ".cl1", ".sc1", ".cl2", ".sc2", ".pg0", ".pg1", ".pg2"];
	magic      = ["Paintworks"];
	converters = ["recoil2png[format:CL1,PG0,SC0,PG.Sc,SC2.Sc,CL0,SC1,CL2]"];
}
