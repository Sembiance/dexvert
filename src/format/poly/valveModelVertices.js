import {Format} from "../../Format.js";

export class valveModelVertices extends Format
{
	name        = "Valve Studio Model Vertices";
	website     = "http://fileformats.archiveteam.org/wiki/Valve_Vertex_Data";
	ext         = [".vvd"];
	magic       = ["Valve Studio Model Vertex Data", "Format: VVD"];
	unsupported = true;
	notes       = "I think this is only useful when paired with some aux files, but I didn't really investigate any further.";
}
