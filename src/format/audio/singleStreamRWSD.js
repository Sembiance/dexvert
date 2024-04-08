import {Format} from "../../Format.js";

export class singleStreamRWSD extends Format
{
	name       = "Single Stream RWSD";
	ext        = [".rwsd"];
	magic      = ["RWSD Audio Stream"];
	converters = ["vgmstream"];
}
