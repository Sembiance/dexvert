import {Format} from "../../Format.js";

export class bmp extends Format
{
	name           = "Bitmap Image";
	website        = "http://fileformats.archiveteam.org/wiki/BMP";
	ext            = [".bmp", ".rle", ".dib", ".pic"];
	forbidExtMatch = [".pic"];	// PIC is so very common for weird odd formats, so no need to run it through the converters unless it matches a magic
	mimeType       = "image/bmp";
	magic          = ["Windows Bitmap", "PC bitmap, Windows 3.x format", "Device independent bitmap graphic", "Run Length Encoded bitmap", "Mac BMP bitmap (MacBinary)", "Bitmap Bild (Typ 3", /^fmt\/(114|116|118|119)( |$)/];
	weakMagic      = ["Windows Bitmap (generic)"];
	metaProvider   = ["image"];
	converters     = dexState =>
	{
		const r = [];
		if(dexState.hasMagics("Mac BMP bitmap (MacBinary)"))
			r.push("deark[mac][deleteADF][convertAsExt:.bmp]");
		r.push("convert", "iio2png", "deark[module:bmp]", "iconvert", "gimp", "nconvert", "ffmpeg[format:bmp_pipe][outType:png]");
		r.push("graphicWorkshopProfessional", "photoDraw");
		r.push(...["keyViewPro", "imageAlchemy", "hiJaakExpress", "corelPhotoPaint", "canvas", "tomsViewer", "pv[strongMatch]"].map(v => `${v}[strongMatch]`));
		return r;
	};
}
