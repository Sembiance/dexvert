import {Format} from "../../Format.js";

export class masterTracksPro extends Format
{
	name        = "Master Tracks Pro";
	ext         = [".mts"];
	magic       = ["Master Tracks Score"];
	unsupported = true;
}
