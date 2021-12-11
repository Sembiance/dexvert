import {Format} from "../../Format.js";

export class zbasic extends Format
{
	name        = "ZBASIC";
	ext         = [".bas"];
	magic       = ["ZBasic DOS source code"];
	unsupported = true;
}
