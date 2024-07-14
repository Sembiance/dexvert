import {Format} from "../../Format.js";

export class turboCalc extends Format
{
	name        = "TurboCalc Document";
	ext         = [".tcd"];
	magic       = ["TurboCalc Document", /^fmt\/1585( |$)/];
	unsupported = true;
}
