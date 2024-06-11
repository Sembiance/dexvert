import {Format} from "../../Format.js";

export class scre2bPacked extends Format
{
	name       = "SCRE2B Packed";
	magic      = ["Packer: SCRE2B"];
	packed     = true;
	converters = ["descre2b"];
}
