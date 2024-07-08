import {Format} from "../../Format.js";

export class packerPacked extends Format
{
	name       = "Packer Packed";
	magic      = ["Packer: Packer"];
	packed     = true;
	converters = ["cup386"];
}
