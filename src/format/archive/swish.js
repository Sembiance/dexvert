import {Format} from "../../Format.js";

export class swish extends Format
{
	name       = "SWiSH Movie";
	website    = "http://fileformats.archiveteam.org/wiki/SWiSH_Movie";
	ext        = [".swi"];
	magic      = [/^fmt\/1865( |$)/];
	converters = ["swish"];
}