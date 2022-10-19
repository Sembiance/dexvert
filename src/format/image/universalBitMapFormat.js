import {Format} from "../../Format.js";

export class universalBitMapFormat extends Format
{
	name           = "Universal BitMap Format";
	website        = "http://discmaster.textfiles.com/browse/749/HACKER2.mdf/tsoft/bjim040.zip";
	ext            = [".ubf"];
	forbidExtMatch = true;
	magic          = ["Universal BitMap Format"];
	unsupported    = true;
}
