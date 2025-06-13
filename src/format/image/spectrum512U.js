import {Format} from "../../Format.js";

export class spectrum512U extends Format
{
	name       = "Spectrum 512 Uncompressed";
	website    = "http://fileformats.archiveteam.org/wiki/Spectrum_512_formats";
	ext        = [".spu"];
	magic      = ["deark: spectrum512u (Spectrum 512 Uncompressed", "Spectrum 512/4096 :spu:"];
	mimeType   = "image/x-spectrum512-uncompressed";
	converters = ["deark[module:spectrum512u]", "recoil2png", "nconvert[format:spu]", "wuimg"];
	verify     = ({meta}) => meta.colorCount>1;
}
