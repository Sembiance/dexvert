import {Format} from "../../Format.js";

export class threeDStudio extends Format
{
	name       = "3D Studio Mesh";
	website    = "http://fileformats.archiveteam.org/wiki/3DS";
	ext        = [".3ds", ".max"];
	magic      = ["3D Studio model", "3D Studio mesh", /^x-fmt\/19( |$)/];
	converters = ["assimp"];
}
