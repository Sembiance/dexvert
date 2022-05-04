import {Format} from "../../Format.js";

export class autoCADSlideLibrary extends Format
{
	name       = "AutoCAD Slide Library";
	website    = "http://fileformats.archiveteam.org/wiki/AIN";
	ext        = [".slb"];
	magic      = ["AutoCAD Slide Library", /^x-fmt\/104( |$)/];
	converters = ["deark"];
}
