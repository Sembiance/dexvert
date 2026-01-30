import {Format} from "../../Format.js";

export class pcx extends Format
{
	name         = "PC Paintbrush Image";
	website      = "http://fileformats.archiveteam.org/wiki/PCX";
	ext          = [".pcx", ".pcc"];
	mimeType     = "image/x-pcx";
	idMeta       = ({macFileType}) => [".PCX", "PCX ", "PCXx"].includes(macFileType);
	magic        = ["PCX bitmap", "image/vnd.zbrush.pcx", /^PCX ver.* image data/, /^PCX$/, "piped pcx sequence (pcx_pipe)", "deark: pcx (PCX)", "Zsoft Paintbrush :pcx:", /^fmt\/(86|87|88|89|90)( |$)/];
	metaProvider = ["image"];
	converters   = [
		"nconvert[format:pcx]", "convert", "deark[module:pcx]", "iio2png", "gimp", "imconv[format:pcx]", "wuimg[format:pcx]",
		...["paintDotNet", "imageAlchemy", "noesis[type:image]", "graphicWorkshopProfessional", "photoDraw", "hiJaakExpress", "picturePublisher", "konvertor", "corelPhotoPaint", "canvas5", "canvas", "tomsViewer", "corelDRAW", "keyViewPro"].map(v => `${v}[strongMatch]`)
	];
}
