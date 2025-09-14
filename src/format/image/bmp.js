import {Format} from "../../Format.js";

export class bmp extends Format
{
	name           = "Bitmap Image";
	website        = "http://fileformats.archiveteam.org/wiki/BMP";
	ext            = [".bmp", ".rle", ".dib", ".pic"];
	forbidExtMatch = [".pic"];	// PIC is so very common for weird odd formats, so no need to run it through the converters unless it matches a magic
	mimeType       = "image/bmp";
	magic          = [
		"Windows Bitmap", /^PC bitmap, (Windows 3\.x|OS\/2 \d\.x) format/, /^PC bitmap, Windows (98\/2000|95\/NT4)/, "Device independent bitmap graphic", "Run Length Encoded bitmap", "Mac BMP bitmap (MacBinary)",
		"image/x-dib", "piped bmp sequence (bmp_pipe)", "PC bitmap", /Bitmap Bild \(Typ \d/, "image/bmp", "deark: bmp", "deark: dib", /^OS\/2 Bitmap :(bmp|dib|os2|pmsk):$/,
		/^fmt\/(114|115|116|117|118|119)( |$)/, /^x-fmt\/270( |$)/
	];
	idMeta       = ({macFileType, macFileCreator}) => ["BMPp", ".BMP", "BMP_", "BMP ", "BMPf", "BMPM"].includes(macFileType) || (macFileType==="BINA" && macFileCreator==="8BIM");
	metaProvider = ["image"];
	converters   = dexState =>
	{
		const r = [];
		if(dexState.hasMagics("Mac BMP bitmap (MacBinary)"))
			r.push("deark[module:macbinary][mac][deleteADF][convertAsExt:.bmp]");
		r.push("convert", "iio2png", "deark[module:bmp]", "iconvert", "gimp", "nconvert[format:bmp]", "ffmpeg[format:bmp_pipe][outType:png]", "wuimg", "imconv[format:bmp][matchType:magic]");
		r.push(...["noesis[type:image]"].map(v => `${v}[matchType:magic]`));
		r.push(...["paintDotNet", "keyViewPro", "imageAlchemy", "corelPhotoPaint", "canvas[matchType:magic][hasExtMatch]", "tomsViewer"].map(v => `${v}[matchType:magic][strongMatch]`));
		// Not reliable and can produce garbage, even with strong matches with extensions: "graphicWorkshopProfessional", "canvas5", "hiJaakExpress", "pv"
		r.push(...["photoDraw"].map(v => `${v}[matchType:magic][strongMatch][hasExtMatch]`));
		return r;
	};
}
