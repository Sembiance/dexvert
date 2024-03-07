import {Format} from "../../Format.js";

export class lookingGlass extends Format
{
	name       = "Looking Glass Resource";
	ext        = [".res"];
	magic      = ["Looking Glass Resource data", "LG Archiv gefunden"];
	converters = ["gameextractor"];
}
