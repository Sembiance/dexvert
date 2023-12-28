import {Format} from "../../Format.js";

export class gmod extends Format
{
	name        = "GMOD Module";
	website     = "https://www.exotica.org.uk/wiki/MultiPlayer";
	ext         = [".gmod"];
	magic       = ["GMOD format module"];
	unsupported = true;
}
