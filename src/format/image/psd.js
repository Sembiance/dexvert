import {Format} from "../../Format.js";

export class psd extends Format
{
	name         = "Adobe Photoshop";
	website      = "http://fileformats.archiveteam.org/wiki/PSD";
	magic        = [/^Adobe Photoshop [Ii]mage/, /^Adobe Photoshop$/, "Photoshop Bild", /^x-fmt\/92( |$)/];
	idMeta       = ({macFileType}) => macFileType==="8BPS";
	ext          = [".psd"];
	mimeType     = "image/vnd.adobe.photoshop";
	metaProvider = ["image"];

	// I made the decision to just use regular convert, which will extract ALL layers from the PSD.
	// I could in theory just extract the 'main' image by doing: ensuring convert calls with `${filePath}[0]`
	converters = [
		"convert", "iio2png", "gimp", "deark[module:psd]", "iconvert",
		"hiJaakExpress", "corelPhotoPaint", "photoDraw", "canvas5[strongMatch]", "canvas[strongMatch]", "tomsViewer", "picturePublisher"];
}
