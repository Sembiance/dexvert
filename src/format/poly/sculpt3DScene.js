import {Format} from "../../Format.js";

export class sculpt3DScene extends Format
{
	name        = "Sculpt 3D Scene";
	ext         = [".scene"];
	magic       = ["Sculpt 3D Scene"];
	unsupported = true;
	notes       = "A 3D rendering file format. I didn't bother investigating it.";
}
