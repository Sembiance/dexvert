import {xu} from "xu";
import {Format} from "../../Format.js";

export class netpic extends Format
{
	name           = "NETPIC by Jim Tucker";
	website        = "http://fileformats.archiveteam.org/wiki/NETPIC_(Jim_Tucker)";
	ext            = [".com", ".npx"];
	forbidExtMatch = true;
	magic          = ["16bit COM NETPIC converted GIF"];
	converters     = [`dosEXEScreenshot[timeout:${xu.SECOND*15}][frameLoc:95]`];
}
