import {xu} from "xu";
import {Format} from "../../Format.js";

export class dxtMipmap extends Format
{
	name       = "DXT MIPMAP";
	ext        = [".dxtmipmap"];
	magic      = [/^geViewer: STREAM_DXTMIPMAP( |$)/];
	converters = ["gameextractor[renameOut][codes:STREAM_DXTMIPMAP]"];
}
