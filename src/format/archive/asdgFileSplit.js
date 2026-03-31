import {Format} from "../../Format.js";

export class asdgFileSplit extends Format
{
	name        = "ASDG's File Split";
	website     = "https://wiki.amigaos.net/wiki/SPLT_IFF_File_Splitting";
	magic       = ["ASDG's File SPLiTting System"];
	unsupported = true;	// only 67 on discmaster2 and often split across disk images, making it near impossible to re-join
}
