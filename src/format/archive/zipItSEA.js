import {Format} from "../../Format.js";

export class zipItSEA extends Format
{
	name       = "ZipIt SEA";
	magic      = ["ZipIt SEA"];
	converters = ["unar[mac][type:ZipIt SEA]"];
}
