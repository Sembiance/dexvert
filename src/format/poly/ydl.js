import {Format} from "../../Format.js";

export class ydl extends Format
{
	name        = "SGI Yet Another Object Description Language";
	website     = "http://fileformats.archiveteam.org/wiki/SGI_YAODL";
	ext         = [".ydl"];
	magic       = ["SGI YAODL 3d vector data"];
	unsupported = true;
}
