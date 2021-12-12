import {Format} from "../../Format.js";

export class homeAccounts extends Format
{
	name           = "Home Accounts";
	ext            = [".ha", ".ha2"];
	forbidExtMatch = true;
	magic          = ["Home Accounts account"];
	converters     = ["strings"];
}
