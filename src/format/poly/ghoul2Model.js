import {Format} from "../../Format.js";

export class ghoul2Model extends Format
{
	name           = "Ghoul 2 Model";
	website        = "http://fileformats.archiveteam.org/wiki/GLM";
	ext            = [".glm"];
	forbidExtMatch = true;
	magic          = ["Ghoul 2 Model"];
	converters     = ["milkShape3D[format:ghoul2]"];
}
