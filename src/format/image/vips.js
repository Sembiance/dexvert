import {Format} from "../../Format.js";

export class vips extends Format
{
	name           = "VIPS Image";
	ext            = [".v"];
	forbidExtMatch = true;
	magic          = ["VIPS bitmap", /^fmt\/1811( |$)/];
	metaProvider   = ["image"];
	converters     = ["convert"];
}
