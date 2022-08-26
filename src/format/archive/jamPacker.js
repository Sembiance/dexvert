import {Format} from "../../Format.js";

export class jamPacker extends Format
{
	name       = "JAM Packer Compressed File";
	magic      = ["JAM Packer compressed data"];
	packed     = true;
	converters = ["xfdDecrunch"];
}
