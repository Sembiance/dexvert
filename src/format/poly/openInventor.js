import {Format} from "../../Format.js";

export class openInventor extends Format
{
	name       = "SGI Open Inventor Scene Graph";
	ext        = [".iv"];
	magic      = ["SGI Open Inventor Scene Graph", "Open Inventor", "IRIS Inventor", /^fmt\/(832|833)( |$)/];
	converters = ["polyTrans64[format:openInventor]"];
}
