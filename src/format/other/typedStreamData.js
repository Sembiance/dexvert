import {Format} from "../../Format.js";

export class typedStreamData extends Format
{
	name       = "NeXT TypedStream Data";
	magic      = ["NeXT typedstream serialized data", "NeXT/Apple typedstream data"];
	converters = ["strings"];
}
