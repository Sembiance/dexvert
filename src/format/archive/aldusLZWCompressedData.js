import {Format} from "../../Format.js";

export class aldusLZWCompressedData extends Format
{
	name       = "Aldus LZW compressed data";
	magic      = ["Aldus LZW compressed data"];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="ACMP" && macFileCreator==="ALZI";
	converters = ["deark[module:aldus_inst]"];
}
