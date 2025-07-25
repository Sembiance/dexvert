import {xu} from "xu";
import {Format} from "../../Format.js";

export class zxSpectrumSnapshot extends Format
{
	name           = "ZX Spectrum Snapshot";
	ext            = [".sna"];
	forbidExtMatch = true;
	magic          = ["ZX Spectrum Snapshot :zxsna:"];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="Snap" && macFileCreator==="ZXSP";
	converters     = ["nconvert[format:zxsna]"];
}
