import {Format} from "../../Format.js";

export class skyRoadsLZS extends Format
{
	name       = "SkyRoads LZS Graphics";
	ext        = [".lzs"];
	magic      = ["SkyRoads bitmap"];
	weakMagic  = true;
	converters = ["wuimg[format:skyroads]"];
}
