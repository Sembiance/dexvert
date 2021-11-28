import {Format} from "../../Format.js";

export class zxStellar extends Format
{
	name       = "ZX Spectrum Stellar";
	ext        = [".stl"];
	fileSize   = 3072;
	converters = ["recoil2png"];
}
