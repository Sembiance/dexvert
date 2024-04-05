import {Format} from "../../Format.js";

export class cgm extends Format
{
	name       = "Computer Graphics Metafile";
	website    = "http://fileformats.archiveteam.org/wiki/CGM";
	ext        = [".cgm"];
	mimeType   = "image/cgm";
	magic      = ["Computer Graphics Metafile", "binary Computer Graphics Metafile", "clear text Computer Graphics Metafile", /^fmt\/(303|306)( |$)/, /^x-fmt\/142( |$)/];
	weakMagic  = true;
	converters = [
		// vector
		"viewCompanion",
		"canvas5[vector]",
		
		// raster
		"keyViewPro", "photoDraw", "corelDRAW", "irfanView", "hiJaakExpress", "picturePublisher", "corelPhotoPaint", "canvas[matchType:magic][nonRaster]"
		
		// vector
		//"soffice[outType:svg]"	// soffice SVG output includes crappy <script> code that only allows the SVG to render when viewed as a webpage (not even an <img> tag works). So it's not even worth including
	];
}
