import {Format} from "../../Format.js";

export class simpleVectorFormat extends Format
{
	name           = "Simple Vector Format";
	website        = "http://fileformats.archiveteam.org/wiki/Simple_Vector_Format";
	ext            = [".svf"];
	forbidExtMatch = true;
	mimeType       = "image/vnd.svf";
	magic          = ["Simple Vector Format", /^fmt\/933( |$)/];
	converters     = [`abydosconvert[format:${this.mimeType}]`];
}
