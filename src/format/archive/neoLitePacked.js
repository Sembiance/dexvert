import {Format} from "../../Format.js";

export class neoLitePacked extends Format
{
	name        = "NeoLite Packed";
	magic       = ["Packer: NeoLite"];
	packed      = true;
	notes       = "Tried (see sandbox/app): RL!dePacker 1.4 & Neo-Executable-Decompressor & neolte20.zip";
	unsupported = true;
}
