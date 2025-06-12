import {Format} from "../../Format.js";

export class fitImage extends Format
{
	name           = "FIT Image";
	ext            = [".fit"];
	forbidExtMatch = true;
	magic          = ["FIT :fit:"];
	converters     = ["nconvert[format:fit]"];
}
