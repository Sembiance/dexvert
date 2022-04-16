import {Format} from "../../Format.js";

export class imagineTexture extends Format
{
	name        = "Imagine Texture";
	website     = "http://fileformats.archiveteam.org/wiki/Imagine_Texture_File";
	ext         = [".itx"];
	magic       = ["Imagine for DOS Texture"];
	unsupported = true;
}
