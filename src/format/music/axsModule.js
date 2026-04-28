import {Format} from "../../Format.js";

export class axsModule extends Format
{
	name           = "AXS Module";
	ext            = [".axs"];
	forbidExtMatch = true;
	magic          = ["AXS module"];
	converters     = ["vibe2wav[renameOut]"];
}
