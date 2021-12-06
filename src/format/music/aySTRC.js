import {Format} from "../../Format.js";

export class aySTRC extends Format
{
	name        = "AY STRC Module";
	ext         = [".strc"];
	magic       = ["AY STRC chiptune"];
	unsupported = true;
}
