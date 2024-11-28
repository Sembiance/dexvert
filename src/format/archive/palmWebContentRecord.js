import {Format} from "../../Format.js";

export class palmWebContentRecord extends Format
{
	name        = "Palm Web Content Record";
	website     = "http://fileformats.archiveteam.org/wiki/Compressed_Markup_Language";
	magic       = ["Palm Web Content Record"];
	weakMagic   = true;
	packed      = true;
	unsupported = true;
	notes       = `
		I could create an extractor for this format, as there doesn't appear to be any out there. These come from extracted palmQueryApplication files from deark.
		See spec here: https://lauriedavis9.tripod.com/copilot/download/Palm_File_Format_Specs.pdf#page=36
		Extra constans here: https://github.com/jichu4n/palm-os-sdk/blob/2592eaafadd803833296dad6bda4b5728ec962d8/sdk-5r4/include/Core/System/CMLConst.h`;
}
