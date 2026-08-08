import {Format} from "../../Format.js";

export class multiMate extends Format
{
	name           = "MultiMate Document";
	website        = "https://winworldpc.com/product/multimate";
	ext            = [".doc", ".dox", ".fnx", ".pat"];
	forbidExtMatch = true;
	magic          = ["MultiMate Advantage II Document", /^x-fmt\/347( |$)/];
	converters     = ["softwareBridge[format:multiMate]", "wordForWord"];
}
