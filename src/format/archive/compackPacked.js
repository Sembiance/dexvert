import {Format} from "../../Format.js";

export class compackPacked extends Format
{
	name       = "COMPACK Packed";
	magic      = ["Packer: COMPACK", "16bit DOS EXE COMPACK compressed"];
	packed     = true;
	converters = ["unp"];
}
