import {Format} from "../../Format.js";

export class sculpt3DScene extends Format
{
	name       = "Sculpt 3D Scene";
	ext        = [".scene"];
	magic      = ["Sculpt 3D Scene"];
	converters = ["threeDObjectConverter"];
}
