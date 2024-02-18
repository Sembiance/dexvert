import {Format} from "../../Format.js";

export class a2HighRes extends Format
{
	name       = "Apple II High Res";
	website    = "http://fileformats.archiveteam.org/wiki/Apple_II_graphics_formats";
	ext        = [".hgr"];
	fileSize   = 8192;
	converters = ["recoil2png"];
}
