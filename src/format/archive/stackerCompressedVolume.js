import {Format} from "../../Format.js";

export class stackerCompressedVolume extends Format
{
	name           = "Stacker compressed volume";
	ext            = [".dsk"];
	forbidExtMatch = true;
	magic          = ["Stacker compressed volume"];
	converters     = ["sevenZip"];
	notes          = "This code might help (I tried the mc extension, couldn't get it to do anything): https://cmp.felk.cvut.cz/~pisa/dmsdos/";
}
