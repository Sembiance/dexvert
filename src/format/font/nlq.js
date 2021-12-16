import {Format} from "../../Format.js";

export class nlq extends Format
{
	name       = "Daisy-Dot";
	ext        = [".nlq"];
	magic      = ["Daisy-Dot NLQ font"];
	notes      = "Most of the sample files do not convert with recoil2png. Maybe a different version?";
	converters = ["recoil2png"];
}
