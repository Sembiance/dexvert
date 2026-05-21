import {Format} from "../../Format.js";

export class amapi3DModel extends Format
{
	name           = "Amapi 3D Model";
	ext            = [".a3d", ".x"];
	forbidExtMatch = true;
	magic          = ["Amapi 3D model"];
	converters     = ["vibe2glb"];
}
