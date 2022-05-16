import {Format} from "../../Format.js";

export class threeDUltraMiniGolfGameData extends Format
{
	name       = "Dynamix Game Data Archive";
	ext        = [".rbx"];
	magic      = ["3D Ultra Mini Golf game data archive"];
	converters = ["gameextractor"];
}
