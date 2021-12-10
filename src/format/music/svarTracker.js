import {Format} from "../../Format.js";

export class svarTracker extends Format
{
	name        = "SVArTracker Module";
	website     = "https://www.kvraudio.com/product/svartracker-by-svar-software";
	ext         = [".svar"];
	magic       = ["SVArTracker module"];
	unsupported = true;
}
