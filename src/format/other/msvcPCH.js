import {Format} from "../../Format.js";

export class msvcPCH extends Format
{
	name       = "Microsoft Visual C PCH file";
	magic      = ["Microsoft Visual C .pch"];
	converters = ["strings"];
}
