import {Format} from "../../Format.js";

export class atariTools800 extends Format
{
	name       = "AtariTools-800";
	website    = "http://fileformats.archiveteam.org/wiki/AtariTools-800";
	ext        = [".agp", ".4pl", ".4pm", ".4mi", ".acs"];
	fileSize   = {".agp" : 7690};
	converters = ["recoil2png[format:AGP,4PL,4PM,4MI,ACS]"];
}
