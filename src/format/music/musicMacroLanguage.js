import {Format} from "../../Format.js";

export class musicMacroLanguage extends Format
{
	name        = "Music Macro Language";
	ext         = [".mus"];
	converters  = ["mml2wav"];
	unsupported = true;
	notes       = "Tried vibe coding a converter, works for most regular DOS BASIC Play type files, but sooo much variety and multiple different platforms. Gave up in the end, though it kinda works. Bigger problem is identification, it's HARD.";
}
