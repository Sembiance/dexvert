import {Format} from "../../Format.js";

export class vcdInfo extends Format
{
	name           = "VCD Info File";
	ext            = [".vcd"];
	forbidExtMatch = true;
	filename       = ["info.vcd"];
	magic          = ["VCD Info File"];
	converters     = ["strings"];
}
