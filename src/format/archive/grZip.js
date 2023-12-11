import {Format} from "../../Format.js";

export class grZip extends Format
{
	name       = "GRZip Compressed Archive";
	ext        = [".grz"];
	magic      = ["GRZip compressed archive"];
	converters = ["GRZip"];
}
