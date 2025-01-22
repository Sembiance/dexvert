import {Format} from "../../Format.js";

export class threeDStudioASE extends Format
{
	name       = "3D Studio ASCII Export";
	website    = "http://fileformats.archiveteam.org/wiki/3DS";
	ext        = [".ase"];
	magic      = ["3D Studio Max ASCII Export file"];
	converters = ["assimp", "threeDObjectConverter", "noesis[type:poly]"];
}
