import {Format} from "../../Format.js";

export class wordMARC extends Format
{
	name        = "WordMARC";
	website     = "https://en.wikipedia.org/wiki/WordMARC";
	ext         = [".wm"];
	unsupported = true;	// no magic identified yet, unlikely to have very many on discmaster, maybe none (due to being VAX based)
	converters  = ["softwareBridge[format:wordMARC]"];
}
