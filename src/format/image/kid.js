import {Format} from "../../Format.js";

export class kid extends Format
{
	name       = "Fullscreen Construction Kit";
	website    = "http://fileformats.archiveteam.org/wiki/Fullscreen_Construction_Kit";
	ext        = [".kid"];
	magic      = ["Fullscreen Construction Kit"];
	fileSize   = 63054;
	converters = ["recoil2png[format:KID]"];
}
