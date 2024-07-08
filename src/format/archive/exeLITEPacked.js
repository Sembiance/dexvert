import {Format} from "../../Format.js";

export class exeLITEPacked extends Format
{
	name       = "ExeLITE Packed";
	magic      = ["ExeLITE compressed 16bit DOS executable"];
	packed     = true;
	converters = ["cup386"];
}
