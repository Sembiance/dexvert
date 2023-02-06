import {Format} from "../../Format.js";

export class msieCache extends Format
{
	name        = "Microsoft Internet Explorer Cache";
	ext         = [".dat"];
	filename    = [/^index\.dat$/i];
	magic       = ["Microsoft Internet Explorer cache", "Internet Explorer cache file"];
	unsupported = true;
	notes       = "Can use this to list contents, but to extract needs to connect to the cache files which is tricky: https://github.com/libyal/libmsiecf";
}
