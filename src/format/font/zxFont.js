import {Format} from "../../Format.js";

export class zxFont extends Format
{
	name       = "ZX Spectrum Font";
	ext        = [".ch4", ".ch6", ".ch8"];
	fileSize   = 2048;
	converters = ["recoil2png"];
}
