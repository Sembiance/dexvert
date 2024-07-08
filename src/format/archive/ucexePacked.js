import {Format} from "../../Format.js";

export class ucexePacked extends Format
{
	name       = "UCEXE Packed";
	magic      = ["Packer: UCEXE", "UCEXE compressed 16bit DOS executable"];
	packed     = true;
	converters = ["unp", "cup386"];
}
