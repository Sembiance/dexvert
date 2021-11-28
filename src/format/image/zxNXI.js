import {Format} from "../../Format.js";

export class zxNXI extends Format
{
	name       = "ZX Spectrum Next Layer 2";
	ext        = [".nxi"];
	fileSize   = 49664;
	converters = ["recoil2png"];
}
