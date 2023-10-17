import {Format} from "../../Format.js";

export class news extends Format
{
	name       = "Newsgroup Content";
	magic      = ["saved news"];	// These additional magics match test/sample/text/txt/*.NN  [/^news, /, /^news$/]  but it's just a single article each so unnews doesn't work on them right now
	converters = ["unnews"];
}
