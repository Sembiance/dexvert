import {Format} from "../../Format.js";

export class rotObject extends Format
{
	name        = "ROT! Object";
	ext         = [".rotobj"];
	magic       = ["ROT Object 3D"];
	unsupported = true;
	notes       = "Only 27 unique files on discmaster. Not sure what program created these files.";
}
