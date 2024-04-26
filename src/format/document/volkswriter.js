import {Format} from "../../Format.js";

export class volkswriter extends Format
{
	name        = "Volkswriter";
	website     = "https://winworldpc.com/product/volkswriter";
	ext         = [".vw"];
	unsupported = true;
	converters  = ["softwareBridge[format:volkswriter3]"];
	notes       = "DOS based word processor. Haven't investigated it for magic.";
}
