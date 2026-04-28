import {Format} from "../../Format.js";

export class maxTrax extends Format
{
	name        = "MaxTrax Module";
	ext         = [".mxtx"];
	magic       = ["MaxTrax module"];
	unsupported = true;	// only 84 unique files on discmaster
}
