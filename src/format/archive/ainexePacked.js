import {Format} from "../../Format.js";

export class ainexePacked extends Format
{
	name       = "AINEXE Packed";
	magic      = ["AINEXE compressed 16bit DOS executable"];
	packed     = true;
	converters = ["cup386"];
}
