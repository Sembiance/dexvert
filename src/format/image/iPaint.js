import {Format} from "../../Format.js";

export class iPaint extends Format
{
	name       = "I Paint";
	ext        = [".ip"];
	magic      = ["Ipaint bitmap"];
	converters = ["recoil2png"]
}
