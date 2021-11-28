import {Format} from "../../Format.js";

export class autoCADSlide extends Format
{
	name       = "AutoCAD Slide";
	website    = "http://fileformats.archiveteam.org/wiki/AutoCAD_Slide";
	ext        = [".sld"];
	magic      = [/^AutoCAD Slide$/];
	converters = ["sldtoppm"];
}
