import {Format} from "../../Format.js";

export class compackPacked extends Format
{
	name       = "COMPACK Packed";
	magic      = ["Packer: COMPACK"];
	packed     = true;
	converters = ["unp"];
}
