import {Format} from "../../Format.js";

export class eaCrowdBanks extends Format
{
	name           = "Electronic Arts Crowd Banks";
	ext            = [".crd"];
	forbidExtMatch = true;
	magic          = ["vgmstream: ea_crdf"];
	converters     = ["vgmstream[types:ea_crdf]"];
}
