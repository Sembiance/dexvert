import {Format} from "../../Format.js";

export class malieGFBitmap extends Format
{
	name       = "MalieGF Bitmap";
	ext        = [".mgf"];
	magic      = ["MalieGF bitmap"];
	converters = ["wuimg[format:png][matchType:magic]"];
}
