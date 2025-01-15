import {Format} from "../../Format.js";

export class gameboyTracker extends Format
{
	name        = "Paragon 5 Gameboy Tracker Module";
	ext         = [".mgb"];
	magic       = ["Paragon 5 Gameboy Tracker module", "Nintendo Gameboy Music Module"];
	unsupported = true;
}
