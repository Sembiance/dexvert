import {Format} from "../../Format.js";

export class metasequoia3DScene extends Format
{
	name       = "Metasequoia 3D Scene";
	ext        = [".mqo"];
	magic      = ["Metasequoia 3D scene"];
	converters = ["threeDObjectConverter"];
}
