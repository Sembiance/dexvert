import {Format} from "../../Format.js";

export class zxNXI extends Format
{
	name       = "ZX Spectrum Next Layer 2";
	website    = "http://fileformats.archiveteam.org/wiki/NXI";
	ext        = [".nxi"];
	fileSize   = 49664;
	converters = ["recoil2png"];
}
