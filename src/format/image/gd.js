import {Format} from "../../Format.js";

export class gd extends Format
{
	name       = "libgd GD Image";
	website    = "http://fileformats.archiveteam.org/wiki/GD_image_format";
	ext        = [".gd"];
	converters = ["gdtopng"];
}
