import {Format} from "../../Format.js";

export class rambrandt extends Format
{
	name       = "RAMbrandt";
	website    = "http://fileformats.archiveteam.org/wiki/RAMbrandt";
	ext        = [".rm0", ".rm1", ".rm2", ".rm3", ".rm4"];
	converters = ["recoil2png[format:RM4,RM3,RM2,RM1,RM0]"];
}
