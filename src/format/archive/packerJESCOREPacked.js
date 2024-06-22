import {Format} from "../../Format.js";

export class packerJESCOREPacked extends Format
{
	name       = "Packer JES //CORE Packed";
	magic      = ["Packer: Packer[1997 by JES //CORE]"];
	packed     = true;
	converters = ["cup386"];
}
