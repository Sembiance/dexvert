import {Format} from "../../Format.js";

export class a2HighRes extends Format
{
	name       = "Apple II High Res";
	ext        = [".hgr"];
	fileSize   = 8192;
	converters = ["recoil2png"];
}
