import {xu} from "xu";
import {Format} from "../../Format.js";
import {_NULL_BYTES_MAGIC} from "../other/nullBytes.js";

export class textWareCDT extends Format
{
	name           = "TextWare CDT File";
	ext            = [".cdt"];
	forbidExtMatch = true;
	magic          = ["TextWare CDT (WEAK)"];
	weakMagic      = true;
	forbiddenMagic = _NULL_BYTES_MAGIC;
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="Ware" && macFileCreator==="TWar";
	converters     = ["strings[hasExtMatch][minBytes:1]"];
}
