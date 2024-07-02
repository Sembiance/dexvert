import {Format} from "../../Format.js";

export class scrnchPacked extends Format
{
	name       = "SCRNCH Packed";
	magic      = ["Packer: SCRNCH"];
	packed     = true;
	converters = ["unp", "cup386"];
}
