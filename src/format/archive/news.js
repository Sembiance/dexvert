import {Format} from "../../Format.js";

export class news extends Format
{
	name       = "Newsgroup Content";
	magic      = ["saved news"];
	converters = ["unnews"];
}
