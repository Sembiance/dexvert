import {Format} from "../../Format.js";

export class plist extends Format
{
	name       = "Apple Property List";
	ext        = [".nib"];
	magic      = [
		// general
		"Apple binary property list", "Mac OS X Binary-format PList", /^fmt\/984( |$)/,
		
		// app specific
		"CoreFoundation binary property list data", "Quartz Composer data", "Safari Web History"
	];
	converters = ["deark[module:plist] & plistutil"];
}
