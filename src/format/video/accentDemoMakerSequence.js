import {Format} from "../../Format.js";

export class accentDemoMakerSequence extends Format
{
	name           = "Accent Software DemoMaker Sequence";
	ext            = [".seq"];
	forbidExtMatch = true;
	magic          = ["Accent DemoMaker Sequence"];
	weakMagic      = true;
	unsupported    = true;
}
