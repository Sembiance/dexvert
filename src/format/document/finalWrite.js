import {Format} from "../../Format.js";

export class finalWrite extends Format
{
	name       = "Final Write Document";
	magic      = ["Final Write document", "IFF data, SWRT Final Copy/Writer document"];
	converters = ["WoW", "strings"];
}
