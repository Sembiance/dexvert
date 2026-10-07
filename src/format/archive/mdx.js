import {Format} from "../../Format.js";

export class mdx extends Format
{
	name       = "Daemon Tools Media Data eXtended Image";
	website    = "http://fileformats.archiveteam.org/wiki/MDX_(Daemon_Tools)";
	ext        = [".mdx"];
	magic      = ["Media Descriptor", "application/x-mdx"];
	weakMagic  = true;
	priority   = this.PRIORITY.TOP;
	converters = ["iat"];	// iat doesn't support "compressed" mdx images (for those, could vibe code a pythong scrupt using libMirage and bchunk) sample compressed mdx: https://archive.org/download/Triada_Russian_CD_Fights_2005/Fights%202005.mdx
}
