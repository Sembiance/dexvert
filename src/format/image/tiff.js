import {Format} from "../../Format.js";

export class tiff extends Format
{
	name         = "Tagged Image File Format";
	website      = "http://fileformats.archiveteam.org/wiki/TIFF";
	ext          = [".tif", ".tiff"];
	mimeType     = "image/tiff";
	magic        = ["Tagged Image File Format", "TIFF image data", "Macintosh TIFF bitmap (MacBinary)", "Macintosh TIFF", /^fmt\/353( |$)/];
	priority     = this.PRIORITY.LOW;	// Often other formats are mis-identified as TIFF files such RAW camera files like Sony ARW and kodak*
	metaProvider = ["image"];

	// Some TIFF files, have invalid properties (hi100.tiff) that causes imagemagick to produce a 'transparent' image, even though there is data in the image. Weird.
	// We can get around it by removing the alpha channel: convert[removeAlpha]
	// But deark doesn't seem to have this issue so we'll stick with it as the first priority
	converters = dexState =>
	{
		const r = [];
		if(dexState.hasMagics("Macintosh TIFF bitmap (MacBinary)"))
			r.push("deark[mac][deleteADF][convertAsExt:.tiff]");
		r.push("deark[module:tiff][noThumbs]", "convert", "iconvert", "iio2png");
		r.push("imageAlchemy", "graphicWorkshopProfessional", "photoDraw", "hiJaakExpress", "imjview", "gimp", "corelPhotoPaint", "canvas", "tomsViewer", "picturePublisher", "corelDRAW", "keyViewPro", "pv[matchType:magic]");
		return r;
	};
}
