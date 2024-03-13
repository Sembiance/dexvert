import {Format} from "../../Format.js";

export class gd2 extends Format
{
	name       = "libgd GD2 Image";
	website    = "http://fileformats.archiveteam.org/wiki/GD2_image_format";
	magic      = ["GDLib Image"];
	ext        = [".gd2"];
	converters = ["gd2topng"];
}
