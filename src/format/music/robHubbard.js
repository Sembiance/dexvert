import {Format} from "../../Format.js";

export class robHubbard extends Format
{
	name         = "Rob Hubbard Module";
	ext          = [".rh", ".rho"];
	magic        = ["Rob Hubbard chiptune", "Rob Hubbard ST module"];
	metaProvider = ["musicInfo"];
	converters   = ["uade123"];
}
