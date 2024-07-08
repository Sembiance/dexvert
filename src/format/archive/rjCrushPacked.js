import {Format} from "../../Format.js";

export class rjCrushPacked extends Format
{
	name       = "RJCrush Packed";
	magic      = ["RJCrush compressed 16bit DOS executable"];
	packed     = true;
	converters = ["cup386"];
}
