import {Format} from "../../Format.js";

export class musicAssembler extends Format
{
	name         = "Music Assembler Module";
	ext          = [".ma"];
	magic        = ["Music Assembler module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
