import {Format} from "../../Format.js";

export class iffHEAD extends Format
{
	name           = "IFF Flow Idea Processor HEAD";
	website        = "https://wiki.amigaos.net/wiki/HEAD_IFF_Flow_Idea_Processor_Format";
	magic          = ["IFF Flow Idea Processor format"];
	converters     = ["iffHEAD2txt"];
}
