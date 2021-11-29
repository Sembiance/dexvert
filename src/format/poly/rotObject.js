import {Format} from "../../Format.js";

export class rotObject extends Format
{
	name        = "ROT! Object";
	ext         = [".rotobj"];
	magic       = ["ROT Object 3D"];
	unsupported = true;
}
