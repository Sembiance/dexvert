import {Format} from "../../Format.js";

export class lbxGameData extends Format
{
	name       = "SimTex LBX Game Data";
	ext        = [".lbx"];
	magic      = ["SimTex LBX game data container"];
	converters = ["gameextractor"];
}
