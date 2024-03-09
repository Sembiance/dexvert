import {Format} from "../../Format.js";

export class dxf extends Format
{
	name       = "Drawing Exchange Format";
	website    = "http://fileformats.archiveteam.org/wiki/DXF";
	ext        = [".dxf"];
	mimeType   = "image/vnd.dxf";
	magic      = [/^AutoCAD Drawing [Ee][Xx]change Format/, "Drawing Interchange File Format", /^fmt\/(63|77|435)( |$)/];
	converters = ["assimp", "blender[format:dxf]"];

	// The converters below are what I used back when this format was treated as an image rather than a 3D model
	// corelDRAW often will just output a blank white image
	/*converters = [
		// vector
		"ezdxf", "soffice[outType:svg][autoCropSVG]", "uniconvertor",
		
		// raster
		"photoDraw", "irfanView",
		
		// raster
		"corelPhotoPaint", "canvas[matchType:magic][nonRaster]"
	];*/
}
