import {Format} from "../../Format.js";

export class fastCAD extends Format
{
	name       = "FastCAD";
	website    = "https://fastcad2.com/";
	ext        = [".fcd"];
	magic      = ["FastCAD drawing"];
	notes      = "Sample SIDE.FCD converts properly, but is detected as garbage by the tensor model, which is proper in this case, it looks like garbage";
	converters = ["fastCAD"]
}
