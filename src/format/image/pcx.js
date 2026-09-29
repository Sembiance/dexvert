import {Format} from "../../Format.js";

export class pcx extends Format
{
	name         = "PC Paintbrush Image";
	website      = "http://fileformats.archiveteam.org/wiki/PCX";
	ext          = [".pcx", ".pcc"];
	mimeType     = "image/x-pcx";
	idMeta       = ({macFileType}) => [".PCX", "PCX ", "PCXx"].includes(macFileType);
	magic        = [
		"PCX bitmap", /^PCX ver.* image data/, /^PCX$/, "piped pcx sequence (pcx_pipe)", "Zsoft Paintbrush :pcx:", /^geViewer: PCX( |$)/, /^fmt\/(86|87|88|89|90)( |$)/,
		
		// marked as weak in WEAK.js (vs weakMagic here) so it'll still match to PCX, but won't trigger strongMatch converters below
		"image/vnd.zbrush.pcx", "deark: pcx (PCX)"
	];
	metaProvider = ["image"];
	converters   = [
		"nconvert[format:pcx]", "convert", "deark[module:pcx]", "iio2png", "gimp[strongMatch]", "imconv[format:pcx]", "wuimg[format:pcx]", "tkimgConvert[strongMatch]", "gameextractor[strongMatch][renameOut][codes:PCX]",
		...["paintDotNet", "imageAlchemy", "noesis[type:image]", "graphicWorkshopProfessional", "photoDraw", "hiJaakExpress", "picturePublisher", "konvertor", "canvas5", "canvas", "tomsViewer", "corelDRAW", "keyViewPro"].map(v => `${v}[strongMatch]`)
	];
}
