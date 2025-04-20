import {Format} from "../../Format.js";

export class aladdinJAM extends Format
{
	name       = "Aladdin JAM Bitmap";
	ext        = [".jam"];
	magic      = ["JAM bitmap"];
	weakMagic  = true;
	converters = ["wuimg"];
}
