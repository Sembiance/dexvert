import {Format} from "../../Format.js";

export class panda3DModel extends Format
{
	name           = "Panda3D Model";
	ext            = [".egg"];
	forbidExtMatch = true;
	magic          = ["Panda3D Model"];
	keepFilename   = true;
	converters     = ["threeDObjectConverter"];
}
