import {Format} from "../../Format.js";

export class palmQueryApplication extends Format
{
	name       = "Palm Query Application";
	website    = "http://fileformats.archiveteam.org/wiki/PQA";
	ext        = [".pqa"];
	magic      = ["Palm Query Application"];
	converters = ["deark[module:palmdb][extractAll]"];
}