import {Format} from "../../Format.js";

export class amapi3DModel extends Format
{
	name        = "Amapi 3D Model";
	ext         = [".a3d", ".x"];
	magic       = ["Amapi 3D model"];
	unsupported = true;
}
