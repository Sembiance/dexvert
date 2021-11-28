import {Format} from "../../Format.js";

export class charPad extends Format
{
	name       = "CharPad";
	website    = "https://subchristsoftware.itch.io/charpad-free-edition";
	ext        = [".ctm"];
	magic      = ["CharPad"];
	converters = ["recoil2png", "view64"];
}
