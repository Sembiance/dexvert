import {Format} from "../../Format.js";

export class starbreezeModel extends Format
{
	name           = "Starbreeze 3D Model";
	ext            = [".xmd"];
	forbidExtMatch = true;
	magic          = ["Starbreeze Model"];
	converters     = ["poly2glb[type:starbreezeModel]"];
}
