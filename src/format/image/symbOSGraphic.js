import {Format} from "../../Format.js";

export class symbOSGraphic extends Format
{
	name       = "SymbOS Graphic";
	website    = "http://fileformats.archiveteam.org/wiki/SymbOS_graphic";
	ext        = [".sgx"];
	converters = ["recoil2png"];
}
