import {Format} from "../../Format.js";

export class halfLifeModel extends Format
{
	name       = "Half Life Model";
	ext        = [".mdl"];
	magic      = ["Half-life Model"];
	converters = ["Crowbar"];
	notes      = "I haven't found a tool to convert an ENTIRE Half Life .mdl into a self-container 3D poly that I can work with, so we extract with crowbar and work with the .smd exports";
}
