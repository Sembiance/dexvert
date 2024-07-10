import {Format} from "../../Format.js";

export class pmgpakPaked extends Format
{
	name       = "PMGPAK Packed";
	magic      = ["Packer: PGMPAK"];
	packed     = true;
	converters = ["unp", "cup386"];
}
