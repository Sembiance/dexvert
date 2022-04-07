import {Format} from "../../Format.js";

export class direct3DObject extends Format
{
	name        = "Direct3D Object";
	ext         = [".x"];
	magic       = ["Microsoft Direct3D Object"];
	unsupported = true;
}
