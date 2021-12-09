import {Format} from "../../Format.js";

export class toc extends Format
{
	name           = "CDRDAO TOC File";
	website        = "http://cdrdao.sourceforge.net/example.html#toc-file-example";
	ext            = [".toc", ".cue"];	// sometimes .toc files are mis-labeled as .cue
	safeExt        = ".toc";
	priority       = this.PRIORITY.LOW;
	forbiddenMagic = ["ISO CDImage cue", "Cue Sheet"];	// don't want to ACTUALLY match .cue files though
	converters     = ["toc2cue"];
}
