import {Format} from "../../Format.js";

export class halfLifeModel extends Format
{
	name           = "Half Life Model";
	ext            = [".mdl"];
	forbidExtMatch = true;
	magic          = ["Half-life Model", "Format: MDL"];
	converters     = ["Crowbar & noesis[type:poly]"];
}
