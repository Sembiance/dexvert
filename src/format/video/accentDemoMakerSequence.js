import {Format} from "../../Format.js";

export class accentDemoMakerSequence extends Format
{
	name           = "Accent Software DemoMaker Sequence";
	ext            = [".seq"];
	forbidExtMatch = true;
	magic          = ["Accent DemoMaker Sequence"];
	weakMagic      = true;
	unsupported    = true;	// 1,059 unique files on discmaster, but this is a very application specific 'animated' type format, not really able to make a converter for it I don't think
}
