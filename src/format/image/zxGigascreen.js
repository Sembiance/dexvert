import {Format} from "../../Format.js";

export class zxGigascreen extends Format
{
	name       = "ZX Spectrum Gigascreen";
	website    = "http://fileformats.archiveteam.org/wiki/Gigascreen";
	ext        = [".img"];
	fileSize   = 13824;
	converters = ["recoil2png"];
}
