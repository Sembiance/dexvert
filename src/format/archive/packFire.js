import {Format} from "../../Format.js";

export class packFire extends Format
{
	name       = "Pack-Fire compressed data";
	magic      = ["Pack-Fire compressed data"];
	packed     = true;
	converters = ["xfdDecrunch"];
}
