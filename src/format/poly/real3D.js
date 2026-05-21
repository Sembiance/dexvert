import {Format} from "../../Format.js";

export class real3D extends Format
{
	name           = "Real 3D";
	ext            = [".real", ".obj"];
	forbidExtMatch = true;
	magic          = ["Real 3D ", "IFF data, REAL Real3D rendering"];
	converters     = ["vibe2glb"];
}
