import {Format} from "../../Format.js";

export class interQuakeModel extends Format
{
	name       = "Inter-Quake Model";
	website    = "http://sauerbraten.org/iqm/";
	ext        = [".iqm"];
	magic      = ["Inter-Quake Model"];
	converters = ["assimp", "noesis[type:poly]"];
}
