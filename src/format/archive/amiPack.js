import {Format} from "../../Format.js";

export class amiPack extends Format
{
	name       = "AmiPack Archive";
	ext        = [".ampk"];
	magic      = [/^AmiPack$/];
	converters = ["unar"];
}
