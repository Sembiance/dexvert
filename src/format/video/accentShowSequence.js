import {Format} from "../../Format.js";

export class accentShowSequence extends Format
{
	name           = "Accent Software Show Sequence";
	ext            = [".seq"];
	forbidExtMatch = true;
	magic          = ["Sequence/Show"];
	weakMagic      = true;
	unsupported    = true;	// 433 unique files on discmaster, but very small file sizes, thus likely very applications pecific
	notes          = "Old MS-DOS software. Couldn't find a standalone player/converter, and also probably wasn't very popular.";
}
