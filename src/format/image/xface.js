import {Format} from "../../Format.js";

export class xface extends Format
{
	name       = "X-face Image";
	magic      = ["deark: xface"];
	converters = ["deark[module:xface]"];
}
