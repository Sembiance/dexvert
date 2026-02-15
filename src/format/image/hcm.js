import {Format} from "../../Format.js";

export class hcm extends Format
{
	name       = "Hard Color Map";
	ext        = [".hcm"];
	magic      = ["Hard Color Map bitmap"];
	fileSize   = 8208;
	converters = ["recoil2png[format:HCM]"];
}
