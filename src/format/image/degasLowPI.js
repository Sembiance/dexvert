import {Format} from "../../Format.js";

export class degasLowPI extends Format
{
	name      = "Degas Low Resolution Picture (PI)";
	website   = "http://fileformats.archiveteam.org/wiki/DEGAS_image";
	ext       = [".pi1"];
	mimeType  = "image/x-pi1";
	byteCheck = [{offset : 0, match : [0x00, 0x00]}];

	// abydosconvert hangs on KENSHIN.PI1
	// nconvert fails to handle certain files properly such as alf23.pi1
	converters = ["recoil2png", "wuimg[hasExtMatch]", `abydosconvert[format:${this.mimeType}]`, "nconvert"];
}
