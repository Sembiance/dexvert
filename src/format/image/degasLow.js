import {Format} from "../../Format.js";

export class degasLow extends Format
{
	name       = "Degas Low Resolution Picture";
	website    = "http://fileformats.archiveteam.org/wiki/DEGAS_image";
	ext        = [".pc1"];
	mimeType   = "image/x-pc1";
	magic      = ["DEGAS low-res compressed bitmap"];
	byteCheck  = [{offset : 0, match : [0x80, 0x00]}];
	converters = ["recoil2png", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
	classify   = true;
}
