import {Format} from "../../Format.js";

export class celestia3DModel extends Format
{
	name       = "Celestia 3D model";
	ext        = [".cmod"];
	magic      = ["Celestia 3D model (binary)"];
	converters = ["threeDObjectConverter"];
}
