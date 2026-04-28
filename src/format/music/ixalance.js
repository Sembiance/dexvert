import {Format} from "../../Format.js";

export class ixalance extends Format
{
	name        = "Ixalance Module";
	ext         = [".ixs"];
	magic       = ["Ixalance module"];
	unsupported = true;	// only 24 unique files on discmaster
}
