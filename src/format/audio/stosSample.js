import {Format} from "../../Format.js";

export class stosSample extends Format
{
	name        = "STOS Sample";
	website     = "https://en.wikipedia.org/wiki/STOS_BASIC";
	ext         = [".sam"];
	magic       = ["STOS Sample"];
	unsupported = true;
}
