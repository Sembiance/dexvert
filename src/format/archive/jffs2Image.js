import {Format} from "../../Format.js";

export class jffs2Image extends Format
{
	name       = "JFFS2 Filesystem Image";
	magic      = ["JFFS2 filesystem", /^Linux (old )?jffs2 filesystem/];
	converters = ["jefferson"];
}
