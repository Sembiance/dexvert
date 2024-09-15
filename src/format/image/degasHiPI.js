import {Format} from "../../Format.js";

export class degasHiPI extends Format
{
	name      = "Degas High Resolution Picture (PI)";
	website   = "http://fileformats.archiveteam.org/wiki/DEGAS_image";
	ext       = [".pi3", ".suh"];
	mimeType  = "image/x-pi3";
	magic     = ["DEGAS hi-res bitmap"];
	byteCheck = [{offset : 0, match : [0x00, 0x02]}];

	// nconvert messes up with certain files such as vanna5.pi3
	converters = ["recoil2png", "wuimg", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
