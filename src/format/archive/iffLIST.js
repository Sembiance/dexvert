import {xu} from "xu";
import {Format} from "../../Format.js";

export class iffLIST extends Format
{
	name        = "IFF LIST File";
	magic       = ["IFF List file"];
	unsupported = true;
	notes       = xu.trim`
		The IFF LIST files contain 'shared' entries that are used for all chunks in the remainder of the file.
		In theory I could parse this file, and "extract" out by creating seperate files for each major FORM entry inside, making sure to also copy into these files the 'shared' entries, adjusting the resulting FORM lengths as needed.
		Couldn't find any real documentation on the LIST/SSETPROP format. See: https://wiki.amigaos.net/wiki/A_Quick_Introduction_to_IFF`;
}
