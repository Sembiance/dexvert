import {Format} from "../../Format.js";

export class jbig2 extends Format
{
	name         = "Joint Bi-Level Image experts Group 2";
	website      = "http://fileformats.archiveteam.org/wiki/JBIG2";
	ext          = [".jb2", ".jbig2"];
	magic        = ["JBIG2 bitmap"];
	converters   = ["wuimg"];
}
