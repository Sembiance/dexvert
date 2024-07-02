import {Format} from "../../Format.js";

export class icePacked extends Format
{
	name       = "ICE Packed";
	magic      = ["ICE compressed/scrambled DOS Command", "Packer: ICE"];
	packed     = true;
	converters = ["unp"];
}
