import {Format} from "../../Format.js";

export class accentDemoMakerSequence extends Format
{
	name           = "Accent Software DemoMaker Sequence";
	ext            = [".seq"];
	forbidExtMatch = true;
	magic          = ["Accent DemoMaker Sequence"];
	weakMagic      = true;
	unsupported    = true;	// 1,059 unique discmaster files, all are less than 60k and are very application specific 'animated' type format, thus a converter would be difficult and may not produce anything interesting
}
