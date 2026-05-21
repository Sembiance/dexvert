import {Format} from "../../Format.js";

export class granny3DModel extends Format
{
	name           = "Granny 3D Model";
	ext            = [".gr2"];
	forbidExtMatch = true;
	magic          = ["Granny 3D model"];
	converters     = ["vibe2glb"];
}
