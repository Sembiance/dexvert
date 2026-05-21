import {Format} from "../../Format.js";

export class valveModelVertices extends Format
{
	name        = "Valve Studio Model Vertices";
	website     = "http://fileformats.archiveteam.org/wiki/Valve_Vertex_Data";
	ext         = [".vvd"];
	magic       = ["Valve Studio Model Vertex Data", "Format: VVD"];
	unsupported = true;	// 25,000 unique files on discmaster but I think it's only useful with other files and doesn't contain actual polygon data, just vertex data and thus no textures/etc
}
