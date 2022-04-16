import {Format} from "../../Format.js";

export class asdgFileSplit extends Format
{
	name        = "ASDG's File Split";
	website     = "https://wiki.amigaos.net/wiki/SPLT_IFF_File_Splitting";
	magic       = ["ASDG's File SPLiTting System"];
	unsupported = true;
}
