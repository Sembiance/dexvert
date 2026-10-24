import {Format} from "../../Format.js";

export class playStation2INT extends Format
{
	name           = "PlayStation 2 INT Video";
	ext            = [".int"];
	forbidExtMatch = true;
	magic          = ["PlayStation 2 INT (ubiint)", "vgmstream: raw_int"];
	converters     = ["ffmpeg[libre][format:ubiint]"];
}
