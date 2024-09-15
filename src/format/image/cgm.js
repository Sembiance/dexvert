import {Format} from "../../Format.js";

export class cgm extends Format
{
	name       = "Computer Graphics Metafile";
	website    = "http://fileformats.archiveteam.org/wiki/CGM";
	ext        = [".cgm"];
	mimeType   = "image/cgm";
	magic      = ["Computer Graphics Metafile", "binary Computer Graphics Metafile", "clear text Computer Graphics Metafile", /^fmt\/(301|303|304|305|306)( |$)/, /^x-fmt\/142( |$)/];
	idMeta     = ({macFileType}) => macFileType==="CGMm";
	weakMagic  = true;	// this is a pretty blanket statement, but lots of crap converts as CGM even though it's not, and if it fooled the detectors, well... so we just set this to only convert those that also have .cgm extension. sigh.
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
