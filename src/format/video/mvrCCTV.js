import {Format} from "../../Format.js";

export class mvrCCTV extends Format
{
	name           = "MVR CCTV Video";
	ext            = [".mvr"];
	forbidExtMatch = true;
	magic          = ["MVR CCTV (mvr)"];
	converters     = ["ffmpeg[libre][format:mvr]"];
}
