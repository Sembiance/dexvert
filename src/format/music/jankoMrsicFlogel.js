import {Format} from "../../Format.js";

export class jankoMrsicFlogel extends Format
{
	name         = "Janko Mrsic-Flogel Module";
	ext          = [".jmf"];
	magic        = ["Janko Mrsic-Flogel module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
