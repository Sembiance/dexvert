import {Format} from "../../Format.js";

export class cso extends Format
{
	name       = "CISO Compressed ISO";
	website    = "https://en.wikipedia.org/wiki/.CSO";
	ext        = [".cso", ".ciso"];
	mimeType   = "application/x-compressed-iso";
	magic      = ["CISO Compressed ISO CD image"];
	converters = ["sevenZip"];
}
