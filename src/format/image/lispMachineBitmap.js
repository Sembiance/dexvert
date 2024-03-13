import {Format} from "../../Format.js";

export class lispMachineBitmap extends Format
{
	name       = "Lisp Machine Bitmap";
	website    = "http://fileformats.archiveteam.org/wiki/Lisp_Machine_Bitmap";
	ext        = [".lispm"];
	magic      = ["Lisp Machine bit-array-file", "Lisp Machine bitmap"];
	converters = ["lispmtopgm"];
}
