import {Format} from "../../Format.js";

export class fastCAD extends Format
{
	name       = "FastCAD";
	website    = "http://fileformats.archiveteam.org/wiki/FastCAD";
	ext        = [".fcd"];
	magic      = ["FastCAD drawing"];
	notes      = "Sample SIDE.FCD converts properly, but is detected as garbage by the classify garbage model, which is proper in this case, it looks like garbage";
	converters = ["fastCAD"];
}
