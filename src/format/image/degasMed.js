import {Format} from "../../Format.js";

export class degasMed extends Format
{
	name      = "Degas Medium Resolution Picture";
	website   = "http://fileformats.archiveteam.org/wiki/DEGAS_image";
	ext       = [".pc2"];
	mimeType  = "image/x-pc2";
	magic     = ["DEGAS med-res compressed bitmap", "Degas (Medium Resolution - RLE) :degas:"];
	byteCheck = [{offset : 0, match : [0x80, 0x01]}];

	// nconvert & wuimg properly handles aspect ratio
	converters = ["nconvert[format:degas]", "wuimg[hasExtMatch]", `abydosconvert[format:${this.mimeType}]`, "recoil2png"];
	classify   = true;
}
