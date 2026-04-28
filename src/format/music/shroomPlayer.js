import {Format} from "../../Format.js";

export class shroomPlayer extends Format
{
	name        = "ShroomPlayer Module";
	ext         = [".sho"];
	magic       = ["ShroomPlayer module"];
	unsupported = true;	// only 6 unique files on discmaster
}
