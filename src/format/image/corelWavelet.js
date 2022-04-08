import {Format} from "../../Format.js";

export class corelWavelet extends Format
{
	name       = "Corel Wavelet";
	website    = "http://fileformats.archiveteam.org/wiki/Corel_Wavelet";
	ext        = [".wi", ".wvl"];
	magic      = ["Corel Wavelet Compressed bitmap"];
	converters = ["corelPhotoPaint"];
}
