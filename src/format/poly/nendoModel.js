import {Format} from "../../Format.js";

export class nendoModel extends Format
{
	name       = "Nendo Model";
	ext        = [".ndo"];
	magic      = ["Nendo model"];
	converters = ["assimp"];
}
