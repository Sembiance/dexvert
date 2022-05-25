import {Format} from "../../Format.js";

export class mdx extends Format
{
	name       = "Daemon Tools Media Data eXtended Image";
	ext        = [".mdx"];
	magic      = ["Media Descriptor"];
	priority   = this.PRIORITY.TOP;
	converters = ["iat"];
}
