import {Format} from "../../Format.js";

export class vertexBinary extends Format
{
	name        = "Vertex Binary 3D Object";
	ext         = [".3d"];
	magic       = ["Vertex binary 3D object"];
	unsupported = true;
}
