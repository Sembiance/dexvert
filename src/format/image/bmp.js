import {Format} from "../../Format.js";

export class bmp extends Format
{
	name           = "Bitmap Image";
	website        = "http://fileformats.archiveteam.org/wiki/BMP";
	ext            = [".bmp", ".rle", ".dib", ".pic"];
	forbidExtMatch = [".pic"];	// PIC is so very common for weird odd formats, so no need to run it through the converters unless it matches a magic
	mimeType       = "image/bmp";
	magic          = [
		"Windows Bitmap", /^PC bitmap, (Windows 3\.x|OS\/2 \d\.x) format/, /^PC bitmap, Windows (98\/2000|95\/NT4)/, "Device independent bitmap graphic", "Run Length Encoded bitmap", "Mac BMP bitmap (MacBinary)", "Alpha Microsystems Bitmap",
		/Bitmap Bild \(Typ \d/, /^fmt\/(114|115|116|117|118|119)( |$)/, /^x-fmt\/270( |$)/
	];
	idMeta         = ({macFileType}) => ["BMPp", ".BMP", "BMP ", "BMPf"].includes(macFileType);
	weakMagic      = ["Windows Bitmap (generic)"];
	metaProvider   = ["image"];
	converters     = dexState =>
	{
		const r = [];
		if(dexState.hasMagics("Mac BMP bitmap (MacBinary)"))
			r.push("deark[module:macbinary][mac][deleteADF][convertAsExt:.bmp]");
		r.push("convert", "iio2png", "deark[module:bmp]", "iconvert", "gimp", "nconvert", "ffmpeg[format:bmp_pipe][outType:png]", "wuimg", "imconv[format:bmp][matchType:magic]");
		r.push(...["canvas5", "graphicWorkshopProfessional", "photoDraw", "paintDotNet"].map(v => `${v}[matchType:magic]`));
		r.push(...["keyViewPro", "imageAlchemy", "hiJaakExpress", "corelPhotoPaint", "canvas[matchType:magic][hasExtMatch]", "tomsViewer", "pv[strongMatch]"].map(v => `${v}[strongMatch]`));
		return r;
	};
}
