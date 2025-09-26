import {Format} from "../../Format.js";

export class dosCodePageFont extends Format
{
	name           = "DOS Code Page Font";
	ext            = [".cpi", ".cp", ".cpx", ".bin", ".cps"];
	forbidExtMatch = true;
	magic          = ["DOS code page font data", "MS-DOS International Code Page Info", "application/x-font-dos", "deark: cpi (CPI font"];
	converters     = ["deark[module:cpi]"];
}
