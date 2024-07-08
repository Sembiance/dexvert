import {Format} from "../../Format.js";

export class xpackLZCOMPacked extends Format
{
	name       = "XPACK/LZCOM Packed";
	magic      = ["Packer: XPACK/LZCOM"];
	packed     = true;
	converters = ["cup386"];
}
