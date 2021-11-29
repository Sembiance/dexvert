import {Format} from "../../Format.js";

export class moRay extends Format
{
	name        = "MoRay 3D Model";
	ext         = [".mdl"];
	magic       = ["MoRay 3D Model"];
	unsupported = true;
}
