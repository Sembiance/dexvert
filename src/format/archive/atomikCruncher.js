import {Format} from "../../Format.js";

export class atomikCruncher extends Format
{
	name       = "Atomik Cruncher Compressed Data";
	magic      = ["Atomik Cruncher 3 compressed data"];
	packed     = true;
	converters = ["xfdDecrunch"];
}
