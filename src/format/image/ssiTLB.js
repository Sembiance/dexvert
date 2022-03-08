import {Format} from "../../Format.js";

export class ssiTLB extends Format
{
	name           = "SSI Packed Library Image";
	ext            = [".tlb", ".glb"];
	forbidExtMatch = true;
	magic          = ["SSI packed Library format"];
	converters     = ["tlb2bmp"];
}
