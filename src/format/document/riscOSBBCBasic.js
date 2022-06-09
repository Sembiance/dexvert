import {Format} from "../../Format.js";

export class riscOSBBCBasic extends Format
{
	name       = "RISC OS BBC BASIC V Source";
	magic      = ["RISC OS BBC BASIC V source"];
	converters = ["strings"];
}
