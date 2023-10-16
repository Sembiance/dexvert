import {Format} from "../../Format.js";

export class lispMachineBitmap extends Format
{
	name       = "Lisp Machine Bitmap";
	website    = "https://netpbm.sourceforge.net/doc/lispmtopgm.html";
	ext        = [".lispm"];
	magic      = ["Lisp Machine bit-array-file"];
	converters = ["lispmtopgm"];
}
