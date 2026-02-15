import {Format} from "../../Format.js";

export class seuckFont extends Format
{
	name       = "Shoot Em Up Construction Kit Font";
	website    = "http://fileformats.archiveteam.org/wiki/Shoot_'Em_Up_Construction_Kit";
	ext        = [".g"];
	fileSize   = 514;
	notes      = "Only one file format has been located. To prevent false positives it assumes this format is 514 bytes long, always.";
	converters = ["recoil2png[format:G]", "wuimg[format:seuck]"];
}
