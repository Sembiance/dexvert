import {Format} from "../../Format.js";
import {_MACBINARY_MAGIC} from "../archive/macBinary.js";

export class psd extends Format
{
	name           = "Adobe Photoshop";
	website        = "http://fileformats.archiveteam.org/wiki/PSD";
	magic          = [
		/^Adobe Photoshop [Ii]mage/, /^Adobe Photoshop$/, "Photoshop Bild", "image/vnd.adobe.photoshop", "piped psd sequence (psd_pipe)", /^deark: psd \(PS[BD]\)/, /^Adobe Photoshop Document :ps[bd]:/,
		"Photoshop Large Document Format", /^fmt\/996( |$)/, /^x-fmt\/92( |$)/
	];
	idMeta         = ({macFileType}) => macFileType==="8BPS";
	forbiddenMagic = _MACBINARY_MAGIC;
	ext            = [".psd"];
	mimeType       = "image/vnd.adobe.photoshop";
	metaProvider   = ["image"];

	// I made the decision to just use regular convert, which will extract ALL layers from the PSD.
	// I could in theory just extract the 'main' image by doing: ensuring convert calls with `${filePath}[0]`
	converters = [
		"convert", "iio2png", "gimp", "deark[module:psd]", "iconvert", "nconvert[format:psd]",
		"paintDotNet",
		"hiJaakExpress", "corelPhotoPaint", "photoDraw", "canvas5[strongMatch]", "canvas[strongMatch]", "tomsViewer", "picturePublisher"];
}
