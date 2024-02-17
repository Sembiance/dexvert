import {Format} from "../../Format.js";

export class mdx extends Format
{
	name       = "Daemon Tools Media Data eXtended Image";
	website    = "http://fileformats.archiveteam.org/wiki/MDX_(Daemon_Tools)";
	ext        = [".mdx"];
	magic      = ["Media Descriptor"];
	priority   = this.PRIORITY.TOP;
	converters = ["iat"];
}
