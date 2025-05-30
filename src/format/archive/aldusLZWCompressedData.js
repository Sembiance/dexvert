import {Format} from "../../Format.js";

export class aldusLZWCompressedData extends Format
{
	name       = "Aldus LZW compressed data";
	magic      = ["Aldus LZW compressed data", "deark: aldus_inst (Aldus LZW)"];
	idMeta     = ({macFileType, macFileCreator}) => macFileType==="ACMP" && macFileCreator==="ALZI";
	converters = ["deark[module:aldus_inst]"];
}
