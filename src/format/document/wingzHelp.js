import {Format} from "../../Format.js";

export class wingzHelp extends Format
{
	name       = "Wingz Help";
	magic      = [/^Wingz [Hh]elp/];
	converters = ["strings"];
}
