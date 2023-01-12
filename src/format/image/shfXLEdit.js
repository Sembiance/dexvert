import {Format} from "../../Format.js";

export class shfXLEdit extends Format
{
	name        = "SHF-XL Edit";
	ext         = [".shx", ".shf"];
	converters  = ["recoil2png"];
	unsupported = true;
	notes       = "Due to no known magic and how recoil2png will convert ANYTHING, we disable this for now.";
}
