import {Format} from "../../Format.js";

export class quakeModel extends Format
{
	name       = "Quake Model";
	website    = "http://tfc.duke.free.fr/coding/mdl-specs-en.html";
	ext        = [".mdl"];
	magic      = [/^Quake Model$/];
	converters = ["assimp", "threeDObjectConverter", "noesis[type:poly]"];
}
