import {Format} from "../../Format.js";

export class dxf extends Format
{
	name       = "Drawing Exchange Format";
	website    = "http://fileformats.archiveteam.org/wiki/DXF";
	ext        = [".dxf"];
	mimeType   = "image/vnd.dxf";
	magic      = [/^AutoCAD Drawing [Ee][Xx]change Format/, "Drawing Interchange File Format"];
	converters = ["ezdxf", "totalCADConverterX", "irfanView", "soffice[outType:svg][autoCropSVG]", "uniconvertor", "corelPhotoPaint"];
}
