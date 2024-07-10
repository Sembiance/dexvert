import {Format} from "../../Format.js";

export class ainexePacked extends Format
{
	name       = "AINEXE Packed";
	magic      = ["AINEXE compressed 16bit DOS executable", "Packer: AINEXE"];
	packed     = true;
	converters = ["cup386"];
}
