import {Format} from "../../Format.js";

export class a2eDoubleHighRes extends Format
{
	name       = "Apple IIe Double High-Resolution";
	website    = "http://fileformats.archiveteam.org/wiki/Apple_II_graphics_formats";
	ext        = [".dhgr", ".dhr"];
	converters = ["recoil2png"];
}
