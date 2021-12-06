import {Format} from "../../Format.js";

export class onyxMusicFile extends Format
{
	name        = "Onyx Music File Module";
	ext         = [".omf"];
	magic       = ["Onyx Music File module"];
	unsupported = true;
}
