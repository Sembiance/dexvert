import {xu} from "xu";
import {Format} from "../../Format.js";

export class gemResourceFile extends Format
{
	name    = "GEM Resource File";
	website = "http://fileformats.archiveteam.org/wiki/GEM_resource_file";
	ext     = [".rsc"];
	notes   = xu.trim`
		deark fails to work with some RSC file such as daleks.rsc and dungeon.rsc
		Better support could be added by coding my own handler by following the format:
		http://cd.textfiles.com/ataricompendium/BOOK/HTML/APPENDC.HTM#rsc`;
	converters = ["deark"];
	verify     = ({dexState}) => !dexState.ran.find(({programid}) => programid==="deark")?.stdout?.includes("gem rsc, atari");
}
