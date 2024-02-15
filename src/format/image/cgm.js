import {Format} from "../../Format.js";

export class cgm extends Format
{
	name       = "Computer Graphics Metafile";
	website    = "http://fileformats.archiveteam.org/wiki/CGM";
	ext        = [".cgm"];
	mimeType   = "image/cgm";
	magic      = ["Computer Graphics Metafile", /^fmt\/(303|306)( |$)/, /^x-fmt\/142( |$)/];
	weakMagic  = true;

	// soffice SVG output includes crappy <script> code that only allows the SVG to render when viewed as a webpage (not even an <img> tag works)
	// Thus why it's dead last. It also CUTS OFF visually CGM files (like corvette.cgm)
	converters = [
		// vector
		"viewCompanion",
		"keyViewPro",
		
		// raster
		"photoDraw", "corelDRAW", "irfanView", "hiJaakExpress", "picturePublisher", "corelPhotoPaint", "canvas[matchType:magic][nonRaster]",
		
		// vector
		"soffice[outType:svg]"
	];
}
