import {Format} from "../../Format.js";

export class cheatPackerPacked extends Format
{
	name       = "Cheat Packer Packed";
	magic      = ["Packer: Cheat packer"];
	packed     = true;
	converters = ["unp", "cup386"];
}
