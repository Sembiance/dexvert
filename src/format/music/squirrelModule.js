import {Format} from "../../Format.js";

export class squirrelModule extends Format
{
	name        = "Squirrel Module";
	ext         = [".sqm"];
	magic       = ["Squirrel Module"];
	unsupported = true;
}
