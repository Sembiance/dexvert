import {Format} from "../../Format.js";

export class korgSong extends Format
{
	name        = "Korg Song";
	ext         = [".sng"];
	magic       = ["Korg Song file"];
	unsupported = true;
}
