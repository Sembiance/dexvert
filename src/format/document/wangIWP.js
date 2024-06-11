import {Format} from "../../Format.js";

export class wangIWP extends Format
{
	name        = "WANG Integrated Word Processor";
	website     = "https://archive.org/details/wangeditor";
	ext         = [".doc"];
	unsupported = true;
	converters  = ["softwareBridge[format:wangIWP]", "wordForWord"];
	notes       = "DOS based word processor. Haven't investigated it for magic.";
}
