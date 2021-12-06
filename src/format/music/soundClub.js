import {Format} from "../../Format.js";

export class soundClub extends Format
{
	name        = "Sound Club Module";
	ext         = [".sn", ".sn2"];
	magic       = ["Sound Club module", "Sound Club 2 module"];
	unsupported = true;
}
