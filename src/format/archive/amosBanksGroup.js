import {Format} from "../../Format.js";

export class amosBanksGroup extends Format
{
	name       = "AMOS Banks Group";
	ext        = [".abk"];
	magic      = ["AMOS Banks group", "AMOS Basic memory banks", "deark: abk (AMOS AmBs format)"];
	converters = ["dumpamos"];
}
