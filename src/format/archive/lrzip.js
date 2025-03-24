import {Format} from "../../Format.js";

export class lrzip extends Format
{
	name           = "Long Range Zip Archive";
	website        = "http://fileformats.archiveteam.org/wiki/Lrzip";
	ext            = [".lrz"];
	forbidExtMatch = true;
	magic          = ["Long Range Zip compressed", "lrzip compressed data", "application/x-lrzip", /^LRZIP compressed data/];
	converters     = ["lrzip"];
}
