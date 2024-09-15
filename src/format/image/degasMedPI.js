import {Format} from "../../Format.js";

export class degasMedPI extends Format
{
	name      = "Degas Medium Resolution Picture (PI)";
	website   = "http://fileformats.archiveteam.org/wiki/DEGAS_image";
	ext       = [".pi2"];
	mimeType  = "image/x-pi2";
	magic     = ["DEGAS med-res bitmap"];
	weakMagic = true;
	byteCheck = [{offset : 0, match : [0x00, 0x01]}];

	// nconvert properly handles aspect ratio
	converters = ["nconvert", "wuimg", "recoil2png", `abydosconvert[format:${this.mimeType}]`];
}
