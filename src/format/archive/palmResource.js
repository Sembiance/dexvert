import {Format} from "../../Format.js";

export class palmResource extends Format
{
	name       = "Palm Resource";
	website    = "http://fileformats.archiveteam.org/wiki/PRC_(Palm_OS)";
	ext        = [".prc"];
	magic      = ["Palm Pilot executable"];
	converters = ["deark[module:palmrc]"];
}
