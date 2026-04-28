import {Format} from "../../Format.js";

export class leonardsSketchDrawing extends Format
{
	name        = "LEONARD'S Sketch Drawing";
	ext         = [".ogf"];
	magic       = ["LEONARD'S Sketch drawing"];
	unsupported = true;	// only 17 unique files on discmaster, all of which were just included with the program
}
