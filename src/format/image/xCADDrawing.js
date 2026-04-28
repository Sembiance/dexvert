import {Format} from "../../Format.js";

export class xCADDrawing extends Format
{
	name        = "X-CAD Drawing";
	ext         = [".xdr"];
	magic       = ["X-CAD Drawing"];
	unsupported = true;	// only 11 unique files on discmaster
}
