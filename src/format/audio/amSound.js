import {Format} from "../../Format.js";

export class amSound extends Format
{
	name        = "AM Sound";
	magic       = ["AM sound"];
	unsupported = true;	// couldn't find any REAL samples of this on discmaster
}
