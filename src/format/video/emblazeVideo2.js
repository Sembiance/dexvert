import {Format} from "../../Format.js";

export class emblazeVideo2 extends Format
{
	name           = "Emblaze Video 2";
	ext            = [".ev2"];
	forbidExtMatch = true;
	magic          = ["Emblaze Video 2 video", "Emblaze Video/Audio (generic)"];
	converters     = ["vibe2avi"];
}
