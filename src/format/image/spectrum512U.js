import {Format} from "../../Format.js";

export class spectrum512U extends Format
{
	name       = "Spectrum 512 Uncompressed";
	website    = "http://fileformats.archiveteam.org/wiki/Spectrum_512_formats";
	ext        = [".spu"];
	magic      = ["deark: spectrum512u (Spectrum 512 Uncompressed"];
	mimeType   = "image/x-spectrum512-uncompressed";
	converters = ["deark[module:spectrum512u]", "recoil2png"];
	verify     = ({meta}) => meta.colorCount>1;
}
