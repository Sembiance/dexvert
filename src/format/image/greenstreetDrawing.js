import {Format} from "../../Format.js";

export class greenstreetDrawing extends Format
{
	name        = "Greenstreet Drawing";
	ext         = [".art"];
	magic       = ["Greenstreet Art drawing", /^fmt\/1877( |$)/];
	unsupported = true;	// these are clip are vector drawings embedded in msCompount .arf files of which there are only a handful of unique files on discmaster
}
