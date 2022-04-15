import {Format} from "../../Format.js";

export class ps1MemoryCard extends Format
{
	name        = "PS1 Memory Card";
	website     = "https://www.psdevwiki.com/ps3/PS1_Savedata";
	ext         = [".mcr", ".mcd"];
	magic       = ["Playstation Memory Card savestate"];
	unsupported = true;
}
