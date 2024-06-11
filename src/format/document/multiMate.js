import {Format} from "../../Format.js";

export class multiMate extends Format
{
	name        = "MultiMate Document";
	website     = "https://winworldpc.com/product/multimate";
	ext         = [".doc"];
	unsupported = true;
	converters  = ["softwareBridge[format:multiMate]", "wordForWord"];
	notes       = "DOS based word processor. Not sure if there is magic for this or not, haven't tried gathering samples from the various versions of the software available.";
}
