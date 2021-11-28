import {Format} from "../../Format.js";

export class spectrum512U extends Format
{
	name       = "Spectrum 512 Uncompressed";
	website    = "http://fileformats.archiveteam.org/wiki/Spectrum_512_formats";
	ext        = [".spu"];
	mimeType   = "image/x-spectrum512-uncompressed";
	converters = ["recoil2png"];
}
