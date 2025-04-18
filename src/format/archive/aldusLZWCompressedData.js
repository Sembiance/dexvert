import {Format} from "../../Format.js";

export class aldusLZWCompressedData extends Format
{
	name       = "Aldus LZW compressed data";
	magic      = ["Aldus LZW compressed data"];
	converters = ["deark[module:aldus_inst]"];
}
