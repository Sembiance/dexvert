import {Format} from "../../Format.js";

export class someraGraphicFormat extends Format
{
	name       = "Somera Graphic Format";
	ext        = [".sgf"];
	magic      = ["Somera Graphic Format"];
	converters = ["wuimg[format:sgf][matchType:magic]"];
}
