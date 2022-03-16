import {Format} from "../../Format.js";

export class turboPacker extends Format
{
	name       = "Turbo Packer";
	website    = "http://fileformats.archiveteam.org/wiki/Turbo_Packer";
	magic      = ["Turbo Packer compressed data", "TPWM: Turbo Packer"];
	converters = ["ancient", "xfdDecrunch"];
}
