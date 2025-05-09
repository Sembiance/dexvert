import {Format} from "../../Format.js";

export class pageStreamDocument extends Format
{
	name           = "PageStream Document";
	website        = "https://en.wikipedia.org/wiki/PageStream";
	ext            = [".pgs"];
	forbidExtMatch = true;
	magic          = ["PageStream Document", "Atari ST PageStream Document (old)"];
	converters     = ["PageStream", "strings"];
}
