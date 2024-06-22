import {Format} from "../../Format.js";

export class dietPacked extends Format
{
	name       = "Diet Packed";
	magic      = ["Packer: Diet"];
	packed     = true;
	converters = ["unp", "cup386"];
}
