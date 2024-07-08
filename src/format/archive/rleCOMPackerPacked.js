import {Format} from "../../Format.js";

export class rleCOMPackerPacked extends Format
{
	name       = "RLE com-packer Packed";
	magic      = ["Packer: RLE com-packer"];
	packed     = true;
	converters = ["cup386"];
}
