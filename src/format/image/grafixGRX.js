import {Format} from "../../Format.js";

export class grafixGRX extends Format
{
	name           = "Atari Grafix GRX";
	ext            = [".grx"];
	forbidExtMatch = true;
	magic          = ["Grafix GRX"];
	converters     = ["recoil2png"];
}
