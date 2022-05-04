import {Format} from "../../Format.js";

export class simpleVectorFormat extends Format
{
	name        = "Simple Vector Format";
	website     = "http://fileformats.archiveteam.org/wiki/Simple_Vector_Format";
	ext         = [".svf"];
	mimeType    = "image/vnd.svf";
	magic       = ["Simple Vector Format", /^fmt\/933( |$)/];
	unsupported = true;
}
