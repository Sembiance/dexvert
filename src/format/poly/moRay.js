import {Format} from "../../Format.js";

export class moRay extends Format
{
	name           = "MoRay 3D Model";
	ext            = [".mdl"];
	forbidExtMatch = true;
	magic          = ["MoRay 3D Model"];
	unsupported    = true;
	notes          = "A shareware program that sat 'on top' of a required POV-Ray installation. Just like POV-Ray, MoRay is super sensitive to version changes and using the last release v3.5 yielded an error where it stated to use 3.2 to open DOS moray files.";
}
