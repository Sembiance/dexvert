import {Format} from "../../Format.js";

export class scrnchPacked extends Format
{
	name       = "SCRNCH Packed";
	magic      = ["Packer: SCRNCH", "SCRNCH compressed"];
	packed     = true;
	converters = ["unp", "cup386"];
}
