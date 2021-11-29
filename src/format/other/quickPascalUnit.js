import {Format} from "../../Format.js";

export class quickPascalUnit extends Format
{
	name           = "Microsoft QuickPascal Unit";
	ext            = [".qpu"];
	forbidExtMatch = true;
	magic          = ["Microsoft QuickPascal Unit"];
	converters     = ["strings"];
}
