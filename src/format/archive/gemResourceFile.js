import {xu} from "xu";
import {Format} from "../../Format.js";

export class gemResourceFile extends Format
{
	name    = "GEM Resource File";
	website = "http://fileformats.archiveteam.org/wiki/GEM_resource_file";
	ext     = [".rsc"];
	magic   = ["deark: rsc (GEM RSC, Atari)"];
	notes   = xu.trim`
		deark fails to work with some RSC file such as daleks.rsc and dungeon.rsc
		Full format details: http://cd.textfiles.com/ataricompendium/BOOK/HTML/APPENDC.HTM#rsc`;
	converters = ["deark[module:rsc]"];
	verify     = ({dexState}) => !dexState.ran.find(({programid}) => programid==="deark")?.stdout?.includes("gem rsc, atari");
}
