import {Format} from "../../Format.js";

export class eplybndsPoly extends Format
{
	name           = "EPLYBNDS Poly";
	ext            = [".ply"];
	forbidExtMatch = true;
	magic          = ["EPLYBNDS Poly", "GEM RTS engine 3D mesh"];
	converters     = ["poly2glb[type:eplybnds]"];
}
