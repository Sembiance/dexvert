import {Format} from "../../Format.js";

export class optlinkPacked extends Format
{
	name       = "OPTLINK Packed";
	magic      = ["Packer: Optlink"];
	packed     = true;
	converters = ["unp"];
}
