import {Format} from "../../Format.js";

export class a2gs320x extends Format
{
	name       = "Apple IIGS 3200/3201";
	website    = "http://fileformats.archiveteam.org/wiki/Apple_II_graphics_formats";
	ext        = [".3200", ".3201"];
	converters = ["recoil2png[format:SH3.Sh3,SH3.AppleIIShr,SH3.3201,3201]"];
}
