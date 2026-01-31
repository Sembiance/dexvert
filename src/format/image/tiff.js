import {Format} from "../../Format.js";
import {_MACBINARY_MAGIC} from "../archive/macBinary.js";

export class tiff extends Format
{
	name         = "Tagged Image File Format";
	website      = "http://fileformats.archiveteam.org/wiki/TIFF";
	ext          = [".tif", ".tiff", ".xif"];
	mimeType     = "image/tiff";
	magic        = [
		// Generic TIFF files
		"Tagged Image File Format", "TIFF image data", "Macintosh TIFF bitmap (MacBinary)", "image/tiff", "piped tiff sequence (tiff_pipe)", "eXtended Image File Format bitmap", /^deark: tiff \((TIFF|XIFF)\)/, /^(Geo)?TIFF (\((jpeg|Tiled)\) )?:(cpt|stw|tiff):$/,
		/^fmt\/(154|155|353)( |$)/, /^x-fmt\/(387|388|399)( |$)/,

		// App-Specific TIFF files
		"CorelChart chart", "QuickLink II Fax bitmap (new)", "Hasselblad 3F RAW image", "Wang Image File Format bitmap (TIFF with WANG tags)", /^fmt\/(1312|1313|1480)( |$)/
	];
	idMeta       = ({macFileType}) => macFileType==="TIFF";
	priority     = this.PRIORITY.LOW;	// Often other formats are mis-identified as TIFF files such RAW camera files like Sony ARW and kodak*
	metaProvider = ["image"];

	// Some TIFF files, have invalid properties (hi100.tiff) that causes imagemagick to produce a 'transparent' image, even though there is data in the image. Weird.
	// We can get around it by removing the alpha channel: convert[removeAlpha]
	// But deark doesn't seem to have this issue so we'll stick with it as the first priority
	converters = dexState =>
	{
		const r = [];
		if(dexState.hasMagics("Macintosh TIFF bitmap (MacBinary)"))
			r.push("deark[module:macbinary][mac][deleteADF][convertAsExt:.tiff]");
		r.push("deark[module:tiff][noThumbs]", "iconvert", "convert", "iio2png", "wuimg[format:tiff]", "tkimgConvert[matchType:magic]");	// iconvert handles ycbcr-cat.tif properly

		// only include certain long-running windows based converters if we're not dealing with a MacBinary file (archive/macBinary/1Sled Ride.EPS)
		if(!dexState.hasMagics(_MACBINARY_MAGIC))
			r.push("imageAlchemy", "graphicWorkshopProfessional", "photoDraw", "hiJaakExpress", "imjview", "gimp", "corelPhotoPaint", "canvas", "tomsViewer", "picturePublisher", "corelDRAW", "keyViewPro", "pv[matchType:magic]");
		return r;
	};
}
