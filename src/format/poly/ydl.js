import {Format} from "../../Format.js";

export class ydl extends Format
{
	name        = "SGI Yet Another Object Description Language";
	website     = "http://fileformats.archiveteam.org/wiki/SGI_YAODL";
	ext         = [".ydl"];
	magic       = ["SGI YAODL 3d vector data", /^fmt\/1663( |$)/];
	unsupported = true;
	notes       = "Very rare format. Less than 20 examples of it in the wild, no known converter for it.";
}
