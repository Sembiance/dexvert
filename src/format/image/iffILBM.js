import {xu} from "xu";
import {Format} from "../../Format.js";

export class iffILBM extends Format
{
	name           = "IFF Interleaved Bitmap Image";
	website        = "http://fileformats.archiveteam.org/wiki/ILBM";
	ext            = [".lbm", ".ilbm", ".iff", ".beam", ".dr", ".mp", ".dctv", ".acbm", ".rgbn"];
	forbidExtMatch = true;
	mimeType       = "image/x-ilbm";
	magic          = [
		// generic ILBM
		"IFF InterLeaved BitMap", "IFF data, ILBM interleaved image", "Interchange File Format Interleaved Bitmap", "IFF ILBM bitmap", "IFF Packed Bitmap", "image/x-ilbm", "IFF ILBM (Generic)", "deark: ilbm (IFF-ILBM)", "deark: ilbm (IFF-PBM)",
		"Amiga Interchange Format IFF/ILBM", /^fmt\/338( |$)/,

		// ACBM
		"IFF data, ACBM continuous image", "IFF Amiga Contiguous BitMap", "deark: ilbm (IFF-ACBM)",

		// RGBN
		/^IFF data, RGB.* image$/, /^IFF .* RGB bitmap$/, "deark: ilbm (IFF-RGB8)", "deark: ilbm (IFF-RGBN)",

		// DCTV
		"DCTV encoded ILBM bitmap",

		// others
		"IFF Sliced HAM bitmap",  "IFF Newtek Dynamic HAM bitmap", "IFF Palette Changes HAM bitMap", "IFF Atari ST Interleaved bitmap", "MandelBlitz IFF Mandelbrot bitmap"
	];
	idMeta       = ({macFileType, macFileCreator}) => macFileType==="ILBM" || (macFileType==="IFF " && macFileCreator==="GKON");
	metaProvider = ["image"];
	converters   = ["ilbm2png"];
	/* PREV CONVERTER LIST:
	converters = [
		`recoil2png`,	// recoil2png produces the best still images for iffILBM files
		"deark[module:ilbm]", "ffmpeg[format:iff][outType:png]", "convert", "iio2png", "wuimg[format:ilbm]", "nconvert[format:iff]", "nconvert[format:lbm]",
		//`abydosconvert[format:${this.mimeType}][outType:png]`,		// abydosconvert 'stretches' the pixels to 'mimic' how they originally looked, I don't really like that and doesn't handle certain images correctly such as GINA and foto57
		// "iff_convert",
		"noesis[type:image][matchType:magic]", "hiJaakExpress[matchType:magic][hasExtMatch]", "pv[matchType:magic]", "paintDotNet[matchType:magic][hasExtMatch]"
		//"canvas[matchType:magic]",	WAY too slow and also doesn't seem to handle any ILBM's that all the others miss, so skip it
	];*/
}
