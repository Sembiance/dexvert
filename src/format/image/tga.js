import {Format} from "../../Format.js";

export class tga extends Format
{
	name         = "Truevision Targa Graphic";
	website      = "http://fileformats.archiveteam.org/wiki/TGA";
	ext          = [".tga", ".targa", ".tpic", ".icb", ".vda", ".vst"];
	mimeType     = "image/x-tga";
	magic        = ["Truevision TGA", "Targa image data", "image/x-tga", /^fmt\/402( |$)/, /^x-fmt\/367( |$)/];
	idMeta       = ({macFileType, macFileCreator}) => (macFileType==="TPIC" && macFileCreator==="8BIM") || (macFileType==="TARG" && macFileCreator==="GKON");
	metaProvider = ["image"];
	
	// ImageMagick sometimes doesn't detect that a TGA image has been rotated. These other converters seem to do a better job at that
	// Only deark, corelDRAW, pv and photoDraw were able to correctly handle flag_b32.tga
	// picturePublisher also supports TGA but bad TGA's have a tendency to cause the program to freeze so bad that the AutoIt script freezes up too (see sandbox/samples/HangsPicturePublisher.tga)
	// abydosconvert sometimes takes garbage files like 'HangsPicturePublisher.tga' and produces garbage output, so we skip that converter too
	// iio2png works really well, except when it doesn't. like 648.TGA and several other hundred TGA's like it, convert as just a transparent image
	converters = [
		"deark[module:tga][strongMatch][opt:tga:trans=0]", "deark[module:tga][matchType:magic][hasExtMatch][opt:tga:trans=0]", "wuimg", "imconv[format:tga][matchType:magic]", "iconvert",
		"imageAlchemy", "paintDotNet",
		"keyViewPro", "corelDRAW", "pv", "photoDraw",
		"nconvert", "recoil2png", "gimp", "iio2png",
		"hiJaakExpress", "corelPhotoPaint", "canvas5", "canvas"
	].map(converter => (["deark", "recoil2png", "iio2png"].some(v => converter.startsWith(v)) ? converter : `${converter}[strongMatch]`));
	// many converters will produce garbage with weak TGA magics. deark too, but if we have an extension+magic match, make an exception. recoil2png and iio2png seem to be pretty strict, so allow those as-is

	// Often files are confused as TGA and it results in just a single solid image. Since TGA's don't appear to have transparecy, require more than 1 color
	// Color counts are calculated for images too large, so we exempt large TGAs from this check since those are encountered in the wild
	verify = ({meta}) => meta.height>2000 || meta.width>2000 || meta.colorCount>1;
}
