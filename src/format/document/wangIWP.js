import {Format} from "../../Format.js";

export class wangIWP extends Format
{
	name        = "WANG Integrated Word Processor";
	website     = "https://archive.org/details/wangeditor";
	ext         = [".doc"];
	unsupported = true;	// no known magic, DOS based word processor
	converters  = ["softwareBridge[format:wangIWP]", "wordForWord"];
}
