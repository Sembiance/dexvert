import {Format} from "../../Format.js";

export class p3c extends Format
{
	name       = "D-GRAPH P3C";
	ext        = [".p3c"];
	converters = ["recoil2png[format:P3C]"];
}
