import {Format} from "../../Format.js";

export class exePackerPacked extends Format
{
	name        = "EXE Packer Packed";
	magic       = ["Packer: EXE Packer"];
	packed      = true;
	unsupported = true;
}
