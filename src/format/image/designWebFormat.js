import {Format} from "../../Format.js";

export class designWebFormat extends Format
{
	name        = "Design Web Format";
	website    = "http://fileformats.archiveteam.org/wiki/DWF";
	ext        = [".dwf", ".dwfx"];
	magic      = ["Autodesk Design Web Format", /^x-fmt\/49( |$)/];

	// viewCompanion can also handle this format AND convert it to SVG, but it does it very poorly and the original intent of the image is lost, so better to just convert to raster
	converters = ["dwg2bmp", "canvas[matchType:magic][nonRaster]"];
}
