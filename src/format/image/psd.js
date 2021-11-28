import {Format} from "../../Format.js";

export class psd extends Format
{
	name         = "Adobe Photoshop";
	website      = "http://fileformats.archiveteam.org/wiki/PSD";
	ext          = [".psd"];
	mimeType     = "image/vnd.adobe.photoshop";
	magic        = [/^Adobe Photoshop [Ii]mage/, /^Adobe Photoshop$/];
	metaProvider = ["image"];

	// I made the decision to just use regular convert, which will extract ALL layers from the PSD.
	// I could in theory just extract the 'main' image by doing: ensuring convert calls with `${filePath}[0]`
	converters   = ["convert"];
}
