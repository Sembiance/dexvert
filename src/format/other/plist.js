import {Format} from "../../Format.js";

export class plist extends Format
{
	name       = "Apple Property List";
	ext        = [".nib"];
	magic      = ["Apple binary property list", "Mac OS X Binary-format PList", "CoreFoundation binary property list data", /^fmt\/984( |$)/];
	converters = ["deark[module:plist] & plistutil"];
}
