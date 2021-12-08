import {Format} from "../../Format.js";

export class hypercard extends Format
{
	name       = "HyperCard Stack";
	website    = "http://fileformats.archiveteam.org/wiki/HyperCard_stack";
	magic      = ["HyperCard Stack"];
	converters = ["hypercard_dasm & stackimport"];
}
