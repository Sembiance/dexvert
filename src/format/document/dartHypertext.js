import {Format} from "../../Format.js";

export class dartHypertext extends Format
{
	name       = "Dart Hypertext";
	magic      = ["Dart hypertext"];
	converters = ["vibe2rtf"];
}
