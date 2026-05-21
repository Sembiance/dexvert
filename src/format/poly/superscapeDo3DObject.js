import {Format} from "../../Format.js";

export class superscapeDo3DObject extends Format
{
	name           = "Superscape Do 3D VCA";
	ext            = [".vca"];
	forbidExtMatch = true;
	magic          = ["Superscape Do 3D object"];
	converters     = ["vibe2glb"];
}
