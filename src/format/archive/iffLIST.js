import {xu} from "xu";
import {Format} from "../../Format.js";

export class iffLIST extends Format
{
	name       = "IFF LIST File";
	website    = "https://wiki.amigaos.net/wiki/A_Quick_Introduction_to_IFF";
	magic      = ["IFF LIST file", "IFF List", "Movie Setter Set"];
	converters = ["unIFFLIST"];
	notes      = xu.trim`
		The IFF LIST files contain 'shared' entries that are used for all chunks in the remainder of the file.
		The VAST MAJORITY of these files are for a program called 'Movie Setter' on the Amiga and contain ILBM's with custom 'FACE' properties.
		I'm not aware of a converter for either the Movie Setter files themselves or the resulting ILBM files sadly.
		But I do properly extract the IFFs from the LIST, so maybe someday I'll find a converter`;
}
