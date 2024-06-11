import {Format} from "../../Format.js";

export class frameworkDocument extends Format
{
	name       = "Framework Document";
	ext        = [".fw2", ".fw3"];
	magic      = [/^Framework.* document/];
	converters = ["wordForWord", "strings[matchType:magic]"];
}
