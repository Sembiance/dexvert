import {Format} from "../../Format.js";

export class halfLifeModel extends Format
{
	name       = "Half Life Model";
	ext        = [".mdl"];
	magic      = ["Half-life Model"];
	converters = ["Crowbar & noesis[type:poly]"];
}
