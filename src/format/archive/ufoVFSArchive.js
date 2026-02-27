import {Format} from "../../Format.js";

export class ufoVFSArchive extends Format
{
	name           = "UFO VFS Archive";
	ext            = [".vfs"];
	forbidExtMatch = true;
	magic          = [/^geArchive: VFS( |$)/, "dragon: VFS "];
	converters     = ["dragonUnpacker[types:VFS]"];	// "gameextractor[codes:VFS]"   This hangs due to a bug in gameextractor, dragon seems to handle them fine
}
