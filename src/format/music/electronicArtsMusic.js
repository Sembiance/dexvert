import {Format} from "../../Format.js";

export class electronicArtsMusic extends Format
{
	name         = "Electronic Arts Music";
	ext          = [".eam"];
	magic        = [/^x-fmt\/137( |$)/];
	weakMagic    = true;
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "vgmstream"];
}
