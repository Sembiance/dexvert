import {Format} from "../../Format.js";

export class wordStarDOS extends Format
{
	name       = "WordStar for DOS Document";
	website    = "http://fileformats.archiveteam.org/wiki/Wordstar";
	magic      = [/^x-fmt\/236( |$)/];
	priority   = this.PRIORITY.LOWEST;
	converters = ["strings"];
}
