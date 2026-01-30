import {Format} from "../../Format.js";

export class quickLinkII extends Format
{
	name           = "QuickLink II Fax";
	ext            = [".qfx"];
	forbidExtMatch = true;
	magic          = ["QuickLink II Fax bitmap"];
	converters     = ["wuimg[format:qfx]"];
}
