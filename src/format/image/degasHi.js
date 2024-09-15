import {Format} from "../../Format.js";

export class degasHi extends Format
{
	name      = "Degas High Resolution Picture";
	website   = "http://fileformats.archiveteam.org/wiki/DEGAS_image";
	ext       = [".pc3"];
	mimeType  = "image/x-pc3";
	magic     = ["DEGAS hi-res compressed bitmap"];
	byteCheck = [{offset : 0, match : [0x80, 0x02]}];
	classify  = true;

	// nconvert fails to properly convert some files
	converters = ["wuimg", "recoil2png", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
