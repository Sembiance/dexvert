import {Format} from "../../Format.js";

export class qpcImage extends Format
{
	name       = "QPC Image";
	ext        = [".qpc"];
	magic      = ["QPC Image"];
	converters = ["qpcvga"];
}
