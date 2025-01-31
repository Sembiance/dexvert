import {Format} from "../../Format.js";

export class lindenBinaryMesh extends Format
{
	name           = "Linden Binary Mesh";
	website        = "https://wiki.secondlife.com/w/index.php?title=Avatar_Appearance#Linden_binary_mesh_file";
	ext            = [".llm"];
	forbidExtMatch = true;
	magic          = ["Linden binary Mesh"];
	converters     = ["threeDObjectConverter"];
}
