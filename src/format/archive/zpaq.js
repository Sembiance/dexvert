import {Format} from "../../Format.js";

export class zpaq extends Format
{
	name       = "ZPAQ Archive";
	website    = "http://fileformats.archiveteam.org/wiki/ZPAQ";
	ext        = [".zpaq"];
	magic      = ["ZPAQ file", "zpaq compressed archive"];
	converters = ["zpaq"];
}