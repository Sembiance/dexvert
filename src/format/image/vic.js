import {Format} from "../../Format.js";

export class vic extends Format
{
	name       = "Commodore 64 VIC";
	ext        = [".vic"];
	converters = ["recoil2png[format:VIC]", "view64"];
}
