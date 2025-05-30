import {Format} from "../../Format.js";

export class zipIt extends Format
{
	name       = "ZipIt";
	magic      = ["ZipIt SEA"];
	converters = ["unar[mac][type:ZipIt SEA]"];
}
