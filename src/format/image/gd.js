import {Format} from "../../Format.js";

export class gd extends Format
{
	name       = "libgd GD Image";
	website    = "https://libgd.github.io/manuals/2.3.0/files/gd_gd-c.html";
	ext        = [".gd"];
	converters = ["gdtopng"];
}
