import {Format} from "../../Format.js";

export class tpackPacked extends Format
{
	name       = "T-PACK Packed";
	magic      = ["Packer: TPACK", "16bit DOS COM T-PACK compressed"];
	packed     = true;
	converters = ["cup386"];
}
