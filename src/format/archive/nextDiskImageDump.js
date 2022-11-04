import {Format} from "../../Format.js";

export class nextDiskImageDump extends Format
{
	name           = "NeXT Disk Image Dump";
	ext            = [".diskimage"];
	forbidExtMatch = true;
	magic          = ["NeXT Disk Image Dump"];
	converters     = ["dd[bs:46][skip:1] -> uniso[nextstep]"];
}
