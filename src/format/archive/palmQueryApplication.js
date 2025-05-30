import {Format} from "../../Format.js";

export class palmQueryApplication extends Format
{
	name       = "Palm Query Application";
	website    = "http://fileformats.archiveteam.org/wiki/PQA";
	ext        = [".pqa"];
	magic      = ["Palm Query Application", "Web Clipping/Palm Query Application", "deark: palmdb (Palm PQA)"];
	converters = ["deark[module:palmdb][extractAll]"];
}
