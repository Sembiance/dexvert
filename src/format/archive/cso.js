import {Format} from "../../Format.js";

export class cso extends Format
{
	name       = "CISO Compressed ISO";
	website    = "https://web.archive.org/web/20230714160428/https://en.wikipedia.org/wiki/.CSO";
	ext        = [".cso", ".ciso"];
	mimeType   = "application/x-compressed-iso";
	magic      = ["CISO Compressed ISO CD image"];
	converters = ["sevenZip"];
}
