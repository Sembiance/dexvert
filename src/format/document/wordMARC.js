import {Format} from "../../Format.js";

export class wordMARC extends Format
{
	name        = "WordMARC";
	website     = "https://en.wikipedia.org/wiki/WordMARC";
	ext         = [".wm"];
	unsupported = true;
	converters  = ["softwareBridge[format:wordMARC]"];
	notes       = "VAX based word processor. Haven't investigated it for magic.";
}
