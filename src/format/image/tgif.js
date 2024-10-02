import {Format} from "../../Format.js";

export class tgif extends Format
{
	name           = "TGIF";
	website        = "https://bourbon.usc.edu/tgif/faq/format.html";
	ext            = [".obj"];
	forbidExtMatch = true;
	magic          = [/^Tgif file/, "application/x-tgif", /^fmt\/1588( |$)/];
	converters     = ["tgif"];
}
