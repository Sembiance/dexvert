import {Format} from "../../Format.js";

export class webExRecording extends Format
{
	name           = "WebEx Recording";
	ext            = [".wrf", ".wot"];
	forbidExtMatch = true;
	magic          = ["WebEx Recording"];
	converters     = ["vibe2avi"];
}
