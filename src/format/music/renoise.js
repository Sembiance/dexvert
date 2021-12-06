import {Format} from "../../Format.js";

export class renoise extends Format
{
	name        = "Renoise Module";
	ext         = [".xrns", ".rns"];
	magic       = ["Renoise module"];
	unsupported = true;
}
