import {Format} from "../../Format.js";

export class shrinkPacked extends Format
{
	name       = "Shrink Packed";
	magic      = ["Shrink packed", "Packer: SHRINK"];
	packed     = true;
	converters = ["unp"];
}
