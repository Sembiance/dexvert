import {Format} from "../../Format.js";

export class dietPacked extends Format
{
	name       = "Diet Packed";
	magic      = ["Packer: Diet", "16bit DOS EXE DIET compressed"];
	packed     = true;
	converters = ["unp", "cup386"];
}
