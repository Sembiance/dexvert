import {Format} from "../../Format.js";

export class homeBrewSound extends Format
{
	name        = "HomeBrew Sound";
	ext         = [".hse"];
	magic       = ["HomeBrew Sound"];
	unsupported = true;	// only 1 unique file on discmaster
}
